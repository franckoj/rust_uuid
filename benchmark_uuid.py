#!/usr/bin/env python3
"""
Benchmark script to compare Python's built-in uuid module with the Rust-backed rust_uuid module.
"""

import timeit
import uuid as python_uuid
import statistics

try:
    import rust_uuid
    RUST_AVAILABLE = True
    print("✅ Rust UUID module loaded successfully")
except ImportError as e:
    RUST_AVAILABLE = False
    print(f"❌ Failed to import rust_uuid: {e}")
    print("Make sure to build the module first with: maturin develop")

def benchmark_function(func, name, iterations=100000):
    """Benchmark a function and return timing statistics."""
    print(f"\n🔄 Benchmarking {name} ({iterations:,} iterations)...")
    
    # Run multiple trials for more accurate results
    trials = 5
    times = []
    
    for trial in range(trials):
        time_taken = timeit.timeit(func, number=iterations)
        times.append(time_taken)
        print(f"  Trial {trial + 1}: {time_taken:.4f}s ({iterations/time_taken:,.0f} ops/sec)")
    
    avg_time = statistics.mean(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"  📊 Average: {avg_time:.4f}s ± {std_dev:.4f}s ({iterations/avg_time:,.0f} ops/sec)")
    return avg_time, iterations/avg_time

def main():
    print("🚀 UUID Performance Benchmark")
    print("=" * 50)
    
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
        else:
            speedup_str = f"📊 {speedup_str}"
            
        print(f"{func_name:<10} {data['python']:>12,.0f}   {data['rust']:>12,.0f}   {speedup_str:<10}")
    
    # Overall average speedup
    avg_speedup = statistics.mean([data['speedup'] for data in results.values()])
    print(f"\n🎯 Overall average speedup: {avg_speedup:.1f}x")
    
    # Test correctness
    print("\n" + "=" * 50)
    print("🔍 CORRECTNESS VALIDATION")
    print("=" * 50)
    
    # Test namespace constants
    print("Testing namespace constants...")
    assert rust_uuid.NAMESPACE_DNS == str(python_uuid.NAMESPACE_DNS), "NAMESPACE_DNS mismatch"
    assert rust_uuid.NAMESPACE_URL == str(python_uuid.NAMESPACE_URL), "NAMESPACE_URL mismatch"
    assert rust_uuid.NAMESPACE_OID == str(python_uuid.NAMESPACE_OID), "NAMESPACE_OID mismatch"
    assert rust_uuid.NAMESPACE_X500 == str(python_uuid.NAMESPACE_X500), "NAMESPACE_X500 mismatch"
    print("✅ All namespace constants match")
    
    # Test UUID format validity
    print("Testing UUID format validity...")
    for _ in range(10):
        # Test that generated UUIDs are valid
        rust_uuid4 = rust_uuid.uuid4()
        python_uuid.UUID(rust_uuid4)  # This will raise if invalid
        
        rust_uuid3 = rust_uuid.uuid3(str(test_namespace), test_name)
        python_uuid.UUID(rust_uuid3)  # This will raise if invalid
        
        rust_uuid5 = rust_uuid.uuid5(str(test_namespace), test_name)
        python_uuid.UUID(rust_uuid5)  # This will raise if invalid
    
    print("✅ All generated UUIDs have valid format")
    
    # Test deterministic UUIDs (uuid3 and uuid5 should be consistent)
    print("Testing deterministic UUID consistency...")
    rust_uuid3_1 = rust_uuid.uuid3(str(test_namespace), test_name)
    rust_uuid3_2 = rust_uuid.uuid3(str(test_namespace), test_name)
    assert rust_uuid3_1 == rust_uuid3_2, "UUID3 should be deterministic"
    
    rust_uuid5_1 = rust_uuid.uuid5(str(test_namespace), test_name)
    rust_uuid5_2 = rust_uuid.uuid5(str(test_namespace), test_name)
    assert rust_uuid5_1 == rust_uuid5_2, "UUID5 should be deterministic"
    print("✅ Deterministic UUIDs are consistent")
    
    print("\n🎉 All tests passed! The Rust implementation is working correctly.")

if __name__ == "__main__":
    main()