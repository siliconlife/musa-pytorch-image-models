#!/bin/bash

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

dtype=(
    "float32"
    "float16"
)

batchs=(
    "1"
    "8"
    "16"
    "32"
    "64"
)

imgsz=(3 224 224)
device="musa"

tag=timm
log_dir="logs"
log_file="bench_${tag}_$(date +%Y%m%d_%H%M%S).log"
if [ ! -d "$log_dir" ]; then
    mkdir "$log_dir"
fi
exec > >(tee -a "$log_dir/$log_file")

for dtype in "${dtype[@]}"; do
    for model in "${models[@]}"; do
        for batch in "${batchs[@]}"; do
            echo "Benchmarking model: ${model} with dtype:${dtype} batch:${batch} imgsz:[${imgsz[*]}]"
            python benchmark.py --device ${device} --bench inference --model ${model} --batch-size ${batch} --input-size "${imgsz[@]}" --precision ${dtype}
        done
    done
done