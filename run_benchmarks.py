#!/usr/bin/env python
# -----------------------------------------------------------------------------
# File:         run_benchmarks.py
# Author:       steven
# Email:        coder.wine@gmail.com
# Description:  provide extreamly easy-to-use, effective and efficient tools (X3ET)
# Created:      20241030
# Updated:      20241030
# Version:      1.0.0
# -----------------------------------------------------------------------------

import os
import time
import json
import torch
import torch_musa
import timm
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import CocoDetection
from tqdm import tqdm
import pandas as pd
import numpy as np
from ptflops import get_model_complexity_info

class BenchmarkConfig:
    def __init__(self):
        self.batch_sizes = [1, 4, 16, 64, 128]
        self.model_configs = {
            'resnet18': {'input_sizes': [224, 384], 'default_size': 224},
            'resnet34': {'input_sizes': [224, 384], 'default_size': 224},
            'resnet50': {'input_sizes': [224, 384], 'default_size': 224},
            'resnet101': {'input_sizes': [224, 384], 'default_size': 224},
            'resnet152': {'input_sizes': [224, 384], 'default_size': 224},

            'resnext50_32x4d': {'input_sizes': [224, 384], 'default_size': 224},
            'resnext101_32x8d': {'input_sizes': [224, 384], 'default_size': 224},

            'densenet121': {'input_sizes': [224, 384], 'default_size': 224},
            'densenet169': {'input_sizes': [224, 384], 'default_size': 224},
            'densenet201': {'input_sizes': [224, 384], 'default_size': 224},

            'efficientnet_b0': {'input_sizes': [224, 240], 'default_size': 224},
            'efficientnet_b1': {'input_sizes': [240, 260], 'default_size': 240},
            'efficientnet_b2': {'input_sizes': [260, 288], 'default_size': 260},
            'efficientnet_b3': {'input_sizes': [300, 320], 'default_size': 300},
            'efficientnet_b4': {'input_sizes': [380, 400], 'default_size': 380},
            'efficientnet_b5': {'input_sizes': [456, 476], 'default_size': 456},
            'efficientnet_b6': {'input_sizes': [528, 548], 'default_size': 528},
            'efficientnet_b7': {'input_sizes': [600, 620], 'default_size': 600},

            'efficientnetv2_s': {'input_sizes': [224, 384], 'default_size': 224},
            'efficientnetv2_m': {'input_sizes': [224, 384], 'default_size': 224},
            'efficientnetv2_l': {'input_sizes': [224, 384], 'default_size': 224},

            'mobilenetv2_100': {'input_sizes': [224, 384], 'default_size': 224},
            'mobilenetv3_small_100': {'input_sizes': [224, 384], 'default_size': 224},
            'mobilenetv3_large_100': {'input_sizes': [224, 384], 'default_size': 224},

            'vit_tiny_patch16_224': {'input_sizes': [224], 'default_size': 224},
            'vit_small_patch16_224': {'input_sizes': [224], 'default_size': 224},
            'vit_base_patch16_224': {'input_sizes': [224], 'default_size': 224},
            'vit_large_patch16_224': {'input_sizes': [224], 'default_size': 224},

            'deit_tiny_patch16_224': {'input_sizes': [224], 'default_size': 224},
            'deit_small_patch16_224': {'input_sizes': [224], 'default_size': 224},
            'deit_base_patch16_224': {'input_sizes': [224], 'default_size': 224},

            'swin_tiny_patch4_window7_224': {'input_sizes': [224], 'default_size': 224},
            'swin_small_patch4_window7_224': {'input_sizes': [224], 'default_size': 224},
            'swin_base_patch4_window7_224': {'input_sizes': [224], 'default_size': 224},
            'swin_large_patch4_window7_224': {'input_sizes': [224], 'default_size': 224},

            'convnext_tiny': {'input_sizes': [224, 384], 'default_size': 224},
            'convnext_small': {'input_sizes': [224, 384], 'default_size': 224},
            'convnext_base': {'input_sizes': [224, 384], 'default_size': 224},
            'convnext_large': {'input_sizes': [224, 384], 'default_size': 224},

            'regnet_y_400mf': {'input_sizes': [224, 384], 'default_size': 224},
            'regnet_y_800mf': {'input_sizes': [224, 384], 'default_size': 224},
            'regnet_y_1_6gf': {'input_sizes': [224, 384], 'default_size': 224},
            'regnet_y_3_2gf': {'input_sizes': [224, 384], 'default_size': 224},
            'regnet_y_8gf': {'input_sizes': [224, 384], 'default_size': 224},

            'coatnet_0': {'input_sizes': [224, 384], 'default_size': 224},
            'coatnet_1': {'input_sizes': [224, 384], 'default_size': 224},
            'coatnet_2': {'input_sizes': [224, 384], 'default_size': 224},

            'maxvit_tiny': {'input_sizes': [224, 384], 'default_size': 224},
            'maxvit_small': {'input_sizes': [224, 384], 'default_size': 224},
            'maxvit_base': {'input_sizes': [224, 384], 'default_size': 224},

            'repvgg_a0': {'input_sizes': [224, 384], 'default_size': 224},
            'repvgg_b0': {'input_sizes': [224, 384], 'default_size': 224},
            'repvgg_b1': {'input_sizes': [224, 384], 'default_size': 224},

            'eva_large_patch14_224': {'input_sizes': [224], 'default_size': 224},
            'eva_giant_patch14_224': {'input_sizes': [224], 'default_size': 224}
        }

        self.active_models = [
            'resnet50',
            'resnet101',
            'resnet152',

            'densenet121',
            'mobilenetv2_100',

            'efficientnet_b0',
            'efficientnet_b1',
            'efficientnet_b2',

            'vit_small_patch16_224',
            'vit_base_patch16_224',
            'vit_large_patch16_224'
        ]

        self.num_warmup = 10
        self.num_iterations = 50
        self.device = torch.device('musa' if torch.musa.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')

    def get_input_sizes(self, model_name):
        if model_name in self.model_configs:
            return self.model_configs[model_name]['input_sizes']
        return [224]

    def get_default_size(self, model_name):
        if model_name in self.model_configs:
            return self.model_configs[model_name]['default_size']
        return 224

class CocoDatasetWrapper(CocoDetection):
    def __init__(self, root, annFile, transform=None):
        super().__init__(root, annFile, transform)

    def __getitem__(self, idx):
        img, _ = super().__getitem__(idx)
        return img

def create_dataloader(input_size, batch_size):
    transform = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])

    dataset = CocoDatasetWrapper(
        root='datasets/coco128/images/train2017',
        annFile='datasets/coco128/annotations/instances_train2017.json',
        transform=transform
    )

    return DataLoader(dataset, batch_size=batch_size, shuffle=True,
                     num_workers=4, pin_memory=True)

def measure_inference_time(model, dataloader, config):
    times = []
    model.eval()

    print("Warming up...")
    for i, inputs in enumerate(dataloader):
        if i >= config.num_warmup:
            break
        inputs = inputs.to(config.device)
        with torch.no_grad():
            _ = model(inputs)

    print("Measuring inference time...")
    with torch.no_grad():
        for i, inputs in enumerate(dataloader):
            if i >= config.num_iterations:
                break
            inputs = inputs.to(config.device)

            if config.device.type == 'cuda':
                torch.cuda.synchronize()
            elif config.device.type == 'musa':
                torch.musa.synchronize()

            start_time = time.time()
            _ = model(inputs)

            if config.device.type == 'cuda':
                torch.cuda.synchronize()
            elif config.device.type == 'musa':
                torch.musa.synchronize()

            end_time = time.time()

            times.append(end_time - start_time)

    return {
        'mean': np.mean(times),
        'std': np.std(times),
        'min': np.min(times),
        'max': np.max(times),
        'median': np.median(times)
    }

def format_size(num_bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f}{unit}B"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}PB"

def run_benchmark():
    config = BenchmarkConfig()
    results = []

    for model_name in config.active_models:
        print(f"\nBenchmarking {model_name}...")
        try:
            model = timm.create_model(model_name, pretrained=True)
            model = model.to(config.device)

            input_sizes = config.get_input_sizes(model_name)

            total_params = sum(p.numel() for p in model.parameters())
            print(f"Model parameters: {format_size(total_params * 4)}  ({total_params:,} params)")

            for input_size in input_sizes:
                for batch_size in config.batch_sizes:
                    try:
                        print(f"\nTesting with input_size={input_size}, batch_size={batch_size}")
                        dataloader = create_dataloader(input_size, batch_size)

                        macs, params = get_model_complexity_info(
                            model, (3, input_size, input_size),
                            as_strings=False, print_per_layer_stat=False
                        )

                        timing = measure_inference_time(model, dataloader, config)

                        results.append({
                            'model': model_name,
                            'input_size': input_size,
                            'batch_size': batch_size,
                            'params': params,
                            'macs': macs,
                            'mean_time': timing['mean'],
                            'std_time': timing['std'],
                            'min_time': timing['min'],
                            'max_time': timing['max'],
                            'median_time': timing['median'],
                            'fps': batch_size / timing['mean'],
                            'throughput': batch_size * config.num_iterations / sum(timing['mean'] for _ in range(config.num_iterations))
                        })

                    except Exception as e:
                        print(f"Error benchmarking {model_name} with input_size={input_size}, "
                              f"batch_size={batch_size}: {str(e)}")
                        continue

        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
            continue

    return results

def save_results(results):
    if not results:
        print("No results to save!")
        return

    os.makedirs('benchmark_results', exist_ok=True)

    timestamp = time.strftime('%Y%m%d_%H%M%S')

    df = pd.DataFrame(results)
    csv_path = f'benchmark_results/benchmark_results_{timestamp}.csv'
    df.to_csv(csv_path, index=False)

    json_path = f'benchmark_results/benchmark_results_{timestamp}.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"\nResults saved to {csv_path} and {json_path}")

    print("\nBenchmark Summary:")
    summary = df.groupby(['model', 'input_size', 'batch_size']).agg({
        'fps': ['mean', 'std'],
        'mean_time': ['mean', 'std'],
        'throughput': 'mean'
    }).round(3)

    print(summary)

    summary_path = f'benchmark_results/summary_{timestamp}.csv'
    summary.to_csv(summary_path)
    print(f"\nSummary saved to {summary_path}")

if __name__ == '__main__':
    results = run_benchmark()
    save_results(results)