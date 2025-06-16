#!/usr/bin/env python3
"""
Enhanced benchmark script with optimizations and analysis.
"""

import timeit
import uuid as python_uuid
import statistics
import gc
import sys

try:
    import rust_uuid
    RUST_AVAILABLE = True
    print("✅ Rust UUID module loaded successfully")
except ImportError as e:
    RUST_AVAILABLE = False
    print(f"❌ Failed to import rust_uuid: {e}")
    print("Make sure to build the module first with: maturin develop --release")

def benchmark_function(func, name, iterations=100000, warmup=1000):
    """Benchmark a function with warmup and return timing statistics."""
    print(f"\n🔄 Benchmarking {name} ({iterations:,} iterations)...")
    
    # Warmup
    for _ in range(warmup):
        func()
    
    # Force garbage collection before benchmarking
    gc.collect()
    
    # Run multiple trials for more accurate results
    trials = 5
    times = []
    
    for trial in range(trials):
        # Force garbage collection before each trial
        gc.collect()
        
        time_taken = timeit.timeit(func, number=iterations)
        times.append(time_taken)
        print(f"  Trial {trial + 1}: {time_taken:.4f}s ({iterations/time_taken:,.0f} ops/sec)")
    
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"  📊 Average: {avg_time:.4f}s ± {std_dev:.4f}s ({iterations/avg_time:,.0f} ops/sec)")
    return avg_time, iterations/avg_time

def benchmark_batch_operations():
    """Benchmark batch operations if available."""
    if not RUST_AVAILABLE:
        return
    
    print("\n" + "="*50)
    print("🚀 BATCH OPERATIONS BENCHMARK")
    print("="*50)
    
    batch_sizes = [1000, 10000, 100000]
    
    for batch_size in batch_sizes:
        print(f"\n🔸 Batch size: {batch_size:,}")
        
        # Python batch (using list comprehension)
        def python_batch():
            return [str(python_uuid.uuid4()) for _ in range(batch_size)]
        
        # Rust batch (if available)
        if hasattr(rust_uuid, 'uuid4_batch'):
            def rust_batch():
                return rust_uuid.uuid4_batch(batch_size)
        else:
            def rust_batch():
                return [rust_uuid.uuid4() for _ in range(batch_size)]
        
        py_time, py_ops = benchmark_function(python_batch, f"Python batch ({batch_size:,})", 10, 5)
        rust_time, rust_ops = benchmark_function(rust_batch, f"Rust batch ({batch_size:,})", 10, 5)
        
        speedup = rust_ops / py_ops
        print(f"  🎯 Batch speedup: {speedup:.2f}x")

def profile_memory_usage():
    """Profile memory usage of UUID generation."""
    try:
        import psutil
        import os
        
        print("\n" + "="*50)
        print("🧠 MEMORY USAGE ANALYSIS")
        print("="*50)
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate many UUIDs and measure memory
        n_uuids = 100000
        
        # Python UUID memory usage
        gc.collect()
        start_memory = process.memory_info().rss / 1024 / 1024
        python_uuids = [str(python_uuid.uuid4()) for _ in range(n_uuids)]
        end_memory = process.memory_info().rss / 1024 / 1024
        python_memory_usage = end_memory - start_memory
        
        del python_uuids
        gc.collect()
        
        if RUST_AVAILABLE:
            # Rust UUID memory usage
            start_memory = process.memory_info().rss / 1024 / 1024
            rust_uuids = [rust_uuid.uuid4() for _ in range(n_uuids)]
            end_memory = process.memory_info().rss / 1024 / 1024
            rust_memory_usage = end_memory - start_memory
            
            del rust_uuids
            gc.collect()
            
            print(f"Python memory usage: {python_memory_usage:.2f} MB")
            print(f"Rust memory usage: {rust_memory_usage:.2f} MB")
            print(f"Memory efficiency: {python_memory_usage/rust_memory_usage:.2f}x")
        else:
            print(f"Python memory usage: {python_memory_usage:.2f} MB")
            
    except ImportError:
        print("psutil not available for memory profiling")

def analyze_performance_bottlenecks():
    """Analyze where the performance bottlenecks are."""
    if not RUST_AVAILABLE:
        return
        
    print("\n" + "="*50)
    print("🔍 PERFORMANCE ANALYSIS")
    print("="*50)
    
    # Test different aspects of UUID generation
    iterations = 100000
    
    # Test string conversion overhead
    print("\n🔸 String Conversion Overhead")
    def rust_uuid_no_str():
        # This would be ideal but we can't avoid string conversion in Python
        return rust_uuid.uuid4()
    
    def python_uuid_no_str():
        return str(python_uuid.uuid4())
    
    rust_time, rust_ops = benchmark_function(rust_uuid_no_str, "Rust UUID4 (with string)", iterations)
    py_time, py_ops = benchmark_function(python_uuid_no_str, "Python UUID4 (with string)", iterations)
    
    print(f"  Raw performance difference: {rust_ops/py_ops:.2f}x")
    
    # Test PyO3 call overhead
    print("\n🔸 Function Call Overhead")
    def rust_multiple_calls():
        rust_uuid.uuid4()
        rust_uuid.uuid4()
        rust_uuid.uuid4()
        rust_uuid.uuid4()
        rust_uuid.uuid4()
    
    def python_multiple_calls():
        python_uuid.uuid4()
        python_uuid.uuid4()
        python_uuid.uuid4()
        python_uuid.uuid4()
        python_uuid.uuid4()
    
    rust_time, rust_ops = benchmark_function(rust_multiple_calls, "Rust 5x calls", iterations//5)
    py_time, py_ops = benchmark_function(python_multiple_calls, "Python 5x calls", iterations//5)
    
    print(f"  Call overhead impact: {rust_ops/py_ops:.2f}x")

def main():
    print("🚀 Enhanced UUID Performance Benchmark")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    
    if not RUST_AVAILABLE:
        print("Rust module not available. Only benchmarking Python uuid module.")
        return
    
    iterations = 100000
    results = {}
    
    # Test data for uuid3 and uuid5
    test_namespace = python_uuid.NAMESPACE_DNS
    test_name = "example.com"
    
    # Benchmark UUID1 (time-based)
    print("\n🔸 UUID1 (Time-based)")
    py_time, py_ops = benchmark_function(python_uuid.uuid1, "Python uuid1", iterations)
    rust_time, rust_ops = benchmark_function(rust_uuid.uuid1, "Rust uuid1", iterations)
    results['uuid1'] = {'python': py_ops, 'rust': rust_ops, 'speedup': rust_ops / py_ops}
    
    # Benchmark UUID3 (MD5-based)
    print("\n🔸 UUID3 (MD5-based)")
    py_time, py_ops = benchmark_function(
        lambda: python_uuid.uuid3(test_namespace, test_name), 
        "Python uuid3", iterations
    )
    rust_time, rust_ops = benchmark_function(
        lambda: rust_uuid.uuid3(str(test_namespace), test_name), 
        "Rust uuid3", iterations
    )
    results['uuid3'] = {'python': py_ops, 'rust': rust_ops, 'speedup': rust_ops / py_ops}
    
    # Benchmark UUID4 (random)
    print("\n🔸 UUID4 (Random)")
    py_time, py_ops = benchmark_function(python_uuid.uuid4, "Python uuid4", iterations)
    rust_time, rust_ops = benchmark_function(rust_uuid.uuid4, "Rust uuid4", iterations)
    results['uuid4'] = {'python': py_ops, 'rust': rust_ops, 'speedup': rust_ops / py_ops}
    
    # Benchmark UUID5 (SHA1-based)
    print("\n🔸 UUID5 (SHA1-based)")
    py_time, py_ops = benchmark_function(
        lambda: python_uuid.uuid5(test_namespace, test_name), 
        "Python uuid5", iterations
    )
    rust_time, rust_ops = benchmark_function(
        lambda: rust_uuid.uuid5(str(test_namespace), test_name), 
        "Rust uuid5", iterations
    )
    results['uuid5'] = {'python': py_ops, 'rust': rust_ops, 'speedup': rust_ops / py_ops}
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"{'Function':<10} {'Python (ops/s)':<15} {'Rust (ops/s)':<15} {'Speedup':<10}")
    print("-" * 55)
    
    for func_name, data in results.items():
        speedup_str = f"{data['speedup']:.1f}x"
        if data['speedup'] >= 2.0:
            speedup_str = f"🚀 {speedup_str}"
        elif data['speedup'] >= 1.2:
            speedup_str = f"⚡ {speedup_str}"
        elif data['speedup'] >= 0.8:
            speedup_str = f"📊 {speedup_str}"
        else:
            speedup_str = f"🐌 {speedup_str}"
            
        print(f"{func_name:<10} {data['python']:>12,.0f}   {data['rust']:>12,.0f}   {speedup_str:<10}")
    
    # Overall average speedup
    avg_speedup = statistics.mean([data['speedup'] for data in results.values()])
    print(f"\n🎯 Overall average speedup: {avg_speedup:.1f}x")
    
    # Additional analysis
    analyze_performance_bottlenecks()
    benchmark_batch_operations()
    profile_memory_usage()
    
    # Recommendations
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if avg_speedup < 1.0:
        print("🔍 The Rust implementation is slower than Python. This is likely due to:")
        print("   1. PyO3 function call overhead")
        print("   2. String conversion overhead")
        print("   3. Python's UUID module being implemented in optimized C")
        print("   4. Small operation size making overhead significant")
        print("\n💡 Consider using Rust UUID when:")
        print("   - Generating large batches of UUIDs")
        print("   - Integrating with other Rust components")
        print("   - Memory efficiency is important")
    else:
        print("🎉 The Rust implementation shows good performance!")
        print("   Consider using it for production workloads.")

if __name__ == "__main__":
    main()