# check_gpus.py

import torch
import sys

def main():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    
    if not torch.cuda.is_available():
        print("\nCUDA is NOT available. Check your drivers/CUDA toolkit installation.")
        print("   - NVIDIA driver should be >= 418.xx for GTX 1070")
        print("   - Install matching CUDA toolkit if needed")
        sys.exit(1)
    
    print("\nNumber of GPUs detected:", torch.cuda.device_count())
    
    if torch.cuda.device_count() < 2:
        print("\nOnly one or zero GPUs detected. Check NVIDIA-SMI in terminal.")
        print("Run: nvidia-smi")
    
    print("\nGPU Details:")
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"   GPU {i}: {props.name}")
        print(f"      Compute Capability: {props.major}.{props.minor}")
        print(f"      Total Memory: {props.total_memory // 1024**3} GB")
        print(f"      Multi-Processor Count: {props.multi_processor_count}")
    
    # Simple test: allocate on both GPUs and do a small matmul
    print("\nRunning basic test on both GPUs...")
    try:
        # Create tensors on GPU 0 and GPU 1
        a = torch.randn(5000, 5000, device='cuda:0')
        b = torch.randn(5000, 5000, device='cuda:1')
        
        # Simple operation on each
        c0 = torch.matmul(a, a)
        c1 = torch.matmul(b, b)
        
        print("   Basic operations succeeded on both GPUs.")
        print("   Your dual GTX 1070 setup is ready for PyTorch workloads!")
        
    except Exception as e:
        print("   Test failed:", str(e))
        print("   Possible causes: insufficient memory, driver issue, or PyTorch CUDA mismatch.")

if __name__ == "__main__":
    main()