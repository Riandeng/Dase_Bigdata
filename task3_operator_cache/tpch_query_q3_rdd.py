from pyspark import SparkConf, SparkContext
import os

def parse_line(line):
    fields = line.split('|')
    return tuple(fields)

def count_input_size(rdd):
    return rdd.map(lambda x: len(str(x))).sum()

def analyze_partition_skew(rdd):
    partition_sizes = rdd.mapPartitions(lambda x: [sum(1 for _ in x)]).collect()
    max_size = max(partition_sizes)
    min_size = min(partition_sizes)
    skew_ratio = max_size / min_size if min_size > 0 else float('inf')
    return {
        'max_partition': max_size,
        'min_partition': min_size,
        'skew_ratio': skew_ratio
    }

def main():
    # 初始化 SparkContext
    conf = SparkConf().setAppName("TPCH_Query3_RDD")
    sc = SparkContext(conf=conf)

    try:
        # 加载数据文件
        customer_lines = sc.textFile("hdfs://master:9000/tpch/customer.tbl").map(parse_line)
        orders_lines = sc.textFile("hdfs://master:9000/tpch/orders.tbl").map(parse_line)
        lineitem_lines = sc.textFile("hdfs://master:9000/tpch/lineitem.tbl").map(parse_line)

        # 过滤和准备数据
        # customer: 过滤 BUILDING 市场部门
        customers = customer_lines.filter(lambda x: x[6] == 'BUILDING') \
                                .map(lambda x: (x[0], x))  # key: c_custkey

        # orders: 过滤订单日期 < '1995-03-15'
        orders = orders_lines.filter(lambda x: x[4] < '1995-03-15') \
                           .map(lambda x: (x[1], (x[0], x[4], x[7])))  # key: o_custkey, value: (o_orderkey, o_orderdate, o_shippriority)

        # lineitem: 过滤发货日期 > '1995-03-15'
        lineitems = lineitem_lines.filter(lambda x: x[10] > '1995-03-15') \
                                .map(lambda x: (x[0], (float(x[5]), float(x[6]))))  # key: l_orderkey, value: (l_extendedprice, l_discount)

        # 首先join customer和orders
        customer_orders = customers.join(orders) \
                                 .map(lambda x: (x[1][1][0], (x[1][1][1], x[1][1][2])))  # key: o_orderkey, value: (o_orderdate, o_shippriority)

        # 然后join with lineitem
        joined_all = customer_orders.join(lineitems)

        # 计算revenue并按照要求的键进行分组
        revenues = joined_all.map(lambda x: (
            (x[0], x[1][0][0], x[1][0][1]),  # (l_orderkey, o_orderdate, o_shippriority)
            x[1][1][0] * (1 - x[1][1][1])    # l_extendedprice * (1 - l_discount)
        ))

        # 按键分组并求和
        revenue_sum = revenues.reduceByKey(lambda a, b: a + b)

        # 转换格式并按照revenue降序和o_orderdate升序排序
        result = revenue_sum.map(lambda x: (x[0][0], x[1], x[0][1], x[0][2])) \
                           .sortBy(lambda x: (-x[1], x[2]))

        # 创建表头和结果字符串
        header = "l_orderkey|revenue|o_orderdate|o_shippriority\n"
        header += "-----------------------------------------\n"
        
        # 将结果转换为正确格式的字符串
        result_strings = result.map(lambda x: f"{x[0]}|{x[1]:.2f}|{x[2]}|{x[3]}")
        
        # 收集所有结果
        all_results = result_strings.collect()
        
        # 将结果写入本地文件
        with open('q3_results.txt', 'w') as f:
            f.write(header)
            for row in all_results:
                f.write(row + '\n')
        
        print("Results have been saved to q3_results.txt")

        # 收集性能指标
        # 1. 数据大小统计
        customer_size = count_input_size(customer_lines)
        orders_size = count_input_size(orders_lines)
        lineitem_size = count_input_size(lineitem_lines)
        
        # 2. 数据倾斜分析
        customer_skew = analyze_partition_skew(customers)
        orders_skew = analyze_partition_skew(orders)
        lineitem_skew = analyze_partition_skew(lineitems)
        
        # 保存性能指标
        with open('q3_performance.txt', 'w') as f:
            f.write("Performance Metrics:\n")
            f.write("-" * 50 + "\n")
            
            f.write("\nData Size (MB):\n")
            f.write(f"Customer: {customer_size/1024/1024:.2f}\n")
            f.write(f"Orders: {orders_size/1024/1024:.2f}\n")
            f.write(f"Lineitem: {lineitem_size/1024/1024:.2f}\n")
            
            f.write("\nData Skew Analysis:\n")
            f.write(f"Customer - Max/Min Ratio: {customer_skew['skew_ratio']:.2f}\n")
            f.write(f"Orders - Max/Min Ratio: {orders_skew['skew_ratio']:.2f}\n")
            f.write(f"Lineitem - Max/Min Ratio: {lineitem_skew['skew_ratio']:.2f}\n")

        print("Performance metrics have been saved to q3_performance.txt")

    except Exception as e:
        print(f"Error occurred: {e}")
        raise
    finally:
        sc.stop()

if __name__ == "__main__":
    main()