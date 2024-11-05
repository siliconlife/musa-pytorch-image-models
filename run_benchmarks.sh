#!/bin/bash

device="musa"
# device="cuda"

dtype=(
    "float32"
    "float16"
)

models=(
    "resnet50"
    # "resnet50d"
    # "resnetrs50"
    # "resnetrs101"
    "resnetv2_50"
    "resnetv2_101"
    "efficientnet_b0"
    "efficientnet_b1"
    # "efficientnet_b1_pruned"
    "efficientnet_b2"
    # "efficientnet_b2_pruned"
    "efficientnet_b3"
    # "efficientnet_b3_pruned"
    "efficientnet_b4"
    "efficientnet_b7"
    "mobilenetv2_100"
    "mobilenetv2_140"
    "vgg16"
    # "vgg16_bn"
    "vgg19"
    # "vgg19_bn"
    "densenet121"
    "densenet161"
    "densenet169"
    "densenet201"
    # "inception_resnet_v2"
    "inception_v3"
    "inception_v4"
    # "vit_base_patch16_224"
    # "vit_base_patch16_384"
    # "vit_base_patch32_224"
    # "vit_base_patch32_384"
    # "vit_large_patch16_224"
    # "vit_large_patch16_384"
    # "vit_large_patch32_384"
    # "vit_large_r50_s32_224"
    # "vit_large_r50_s32_384"
    # "vit_small_patch16_224"
    # "vit_small_patch16_384"
    # "vit_small_patch32_224"
    # "vit_small_patch32_384"
    # "vit_small_r26_s32_224"
    # "vit_small_r26_s32_384"
    # "vit_tiny_patch16_224"
    # "vit_tiny_patch16_384"
    # "vit_tiny_r_s16_p8_224"
    # "vit_tiny_r_s16_p8_384"
)

log_dir="./logs"
log_file="benchmark_$(date +%Y%m%d_%H%M%S).log"

mkdir -p $log_dir
exec > >(tee -a "$log_dir/$log_file") 2>&1

for dtype in "${dtype[@]}"
do
    for model in "${models[@]}"
    do
        echo "Running $model with $dtype"
        python benchmark.py --device $device --bench inference --model $model --batch-size 32 --input-size 3 224 224 --precision $dtype
    done
done