import os
from clip_client import Client
from enum import Enum
import ddddocr
import cv2
from dotenv import load_dotenv
import numpy as np
import httpx
from chat import Chat

load_dotenv()


class CaptchaDistinguishType(Enum):
    CLASSIFICATION = 1
    EMBEDDINGS = 2
    VISION = 3


def encode_images(images):
    c = Client(os.getenv("CLIP_URL"))
    encoded_images = c.encode(images)
    return encoded_images


def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    similarity = dot_product / (norm_v1 * norm_v2)
    return similarity


def image_classification(image_path):
    with open(image_path, "rb") as img:
        image_data = img.read()
    headers = {"Authorization": f"Bearer {os.getenv('CF_API_TOKEN')}"}
    data = {"image": list(image_data)}
    response = httpx.post(
        str(os.getenv("CF_API_GATEWAY")) + "@cf/microsoft/resnet-50",
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    if response.is_success:
        return response.json()["result"]
    else:
        return None


def ocr(image_path, path, sort: bool = False):
    det = ddddocr.DdddOcr(det=True)
    with open(image_path, "rb") as f:
        image = f.read()
    poses = det.detection(image)
    im = cv2.imread(image_path)
    i = 0
    if sort:
        poses = sorted(poses, key=lambda box: box[0])
    for box in poses:
        x1, y1, x2, y2 = box
        cv2.imwrite(path + str(i) + ".jpg", im[y1:y2, x1:x2])
        i += 1
    return poses


def calculate_similarity(data1, data2):
    # 创建一个包含两个图像所有标签的集合
    allLabels = set([r["label"] for r in data1] + [r["label"] for r in data2])
    # 根据所有标签创建分数向量
    scoreVector1 = [
        next((item["score"] for item in data1 if item["label"] == label), 0)
        for label in allLabels
    ]
    scoreVector2 = [
        next((item["score"] for item in data2 if item["label"] == label), 0)
        for label in allLabels
    ]
    # 计算余弦相似度
    return cosine_similarity(scoreVector1, scoreVector2)


def cracker(tip_image, img_image, path, type: int):
    optimize_image(img_image, False)
    tip_poses = ocr(tip_image, path + "/" + "tip_", sort=True)
    tip_nums = len(tip_poses)
    img_poses = ocr(img_image, path + "/" + "img_", sort=True)
    img_nums = len(img_poses)
    tip_results = []
    img_results = []
    if type == CaptchaDistinguishType.CLASSIFICATION.value:
        print("tip_nums: " + str(tip_nums))
        print("img_nums: " + str(img_nums))
        for i in range(tip_nums):
            tip_result = image_classification(path + "/" + "tip_" + str(i) + ".jpg")
            if tip_result:
                tip_results.append(tip_result)
        for i in range(img_nums):
            img_result = image_classification(path + "/" + "img_" + str(i) + ".jpg")
            if img_result:
                img_results.append(img_result)
    elif type == CaptchaDistinguishType.EMBEDDINGS.value:
        tip_images = []
        for i in range(tip_nums):
            tip_images.append(path + "/" + "tip_" + str(i) + ".jpg")
        tip_results = encode_images(tip_images)
        img_images = []
        for i in range(img_nums):
            optimize_image(path + "/" + "img_" + str(i) + ".jpg", True)
            img_images.append(path + "/" + "img_" + str(i) + ".jpg")
        img_results = encode_images(img_images)
    click_results = []
    used_indices = set()
    for i in range(tip_nums):
        max_similarity = -1.0
        img_index = 0
        for j in range(img_nums):
            if j in used_indices:
                continue
            if type == CaptchaDistinguishType.CLASSIFICATION.value:
                similarity_result = calculate_similarity(tip_results[i], img_results[j])
            elif type == CaptchaDistinguishType.EMBEDDINGS.value:
                similarity_result = cosine_similarity(tip_results[i], img_results[j])
            elif type == CaptchaDistinguishType.VISION.value:
                chat = Chat()
                similarity_result = chat.compare_image(
                    path + "/" + "tip_" + str(i) + ".jpg",
                    path + "/" + "img_" + str(j) + ".jpg",
                )
            if similarity_result > max_similarity:
                max_similarity = similarity_result
                img_index = j
        click_results.append(img_poses[img_index])
        used_indices.add(img_index)
    return click_results


def optimize_image(image_path, gray: bool):
    # 使用OpenCV加载图像
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    # 检查图像通道数，如果是4通道（RGBA）则抛弃Alpha通道
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    cv2.imwrite(image_path, img)
    if gray:
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 直方图均衡化增强对比度
        equalized_gray = cv2.equalizeHist(gray_image)

        # 应用Canny边缘检测
        edges = cv2.Canny(equalized_gray, threshold1=100, threshold2=200)

        # 应用形态学操作，例如开运算
        kernel = np.ones((5, 5), np.uint8)
        opening = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)

        # 尺寸归一化以匹配模型输入
        size = (224, 224)
        resized_image = cv2.resize(opening, size)

        # 保存处理后的图像到原始路径
        cv2.imwrite(image_path, resized_image)
