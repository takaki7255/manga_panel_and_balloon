import cv2
import os
import numpy as np
import xml.etree.ElementTree as ET


# アノテーションファイルからページごとにオブジェクトのバウンディングボックス情報を取得
def get_baundingbox_info_from_xml(xml_file):
    """
    xmlファイルからページごとにオブジェクトのバウンディングボックス情報を取得
    :param xml_file: アノテーションファイルのパス
    :return: ページごとのオブジェクトのバウンディングボックス情報
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    pages = root.findall(".//page")
    page_objects = {}
    for page in pages:
        page_index = page.get("index")
        # to int
        page_index = int(page_index)
        objects = []

        for obj in page:
            if obj.tag in ["frame", "text", "body", "face"]:
                obj_data = {
                    "type": obj.tag,
                    "id": obj.get("id"),
                    "xmin": obj.get("xmin"),
                    "ymin": obj.get("ymin"),
                    "xmax": obj.get("xmax"),
                    "ymax": obj.get("ymax"),
                }
                objects.append(obj_data)

        page_objects[page_index] = objects

    return page_objects

# アノテーションファイルからページごとにパネルのバウンディングボックス情報を取得
def get_panelbbox_info_from_xml(xml_file):
    """
    xmlファイルからページごとにパネルのバウンディングボックス情報を取得
    :param xml_file: アノテーションファイルのパス
    :return: ページごとのパネルのバウンディングボックス情報
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    pages = root.findall(".//page")
    page_objects = {}
    for page in pages:
        page_index = page.get("index")
        # to int
        page_index = int(page_index)
        objects = []

        for obj in page:
            if obj.tag in ["frame"]:
                obj_data = {
                    "type": obj.tag,
                    "id": obj.get("id"),
                    "xmin": obj.get("xmin"),
                    "ymin": obj.get("ymin"),
                    "xmax": obj.get("xmax"),
                    "ymax": obj.get("ymax"),
                }
                objects.append(obj_data)

        page_objects[page_index] = objects

    return page_objects


# アノテーションファイルからページごとにテキストのバウンディングボックスのみ情報を取得
def get_textbbox_info_from_xml(xml_file):
    """
    xmlファイルからページごとにテキストのバウンディングボックスのみ情報を取得
    :param xml_file: アノテーションファイルのパス
    :return: ページごとのテキストのバウンディングボックス情報
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    pages = root.findall(".//page")
    page_objects = {}
    for page in pages:
        page_index = page.get("index")
        # to int
        page_index = int(page_index)
        objects = []

        for obj in page:
            if obj.tag in ["text"]:
                obj_data = {
                    "type": obj.tag,
                    "id": obj.get("id"),
                    "xmin": obj.get("xmin"),
                    "ymin": obj.get("ymin"),
                    "xmax": obj.get("xmax"),
                    "ymax": obj.get("ymax"),
                }
                objects.append(obj_data)

        page_objects[page_index] = objects

    return page_objects

def get_text_and_frame_bbox_info_from_xml(xml_file):
    """
    xmlファイルからページごとにテキストとフレームのバウンディングボックス情報を取得
    :param xml_file: アノテーションファイルのパス
    :return: ページごとのテキストとフレームのバウンディングボックス情報
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    pages = root.findall(".//page")
    page_objects = {}
    for page in pages:
        page_index = page.get("index")
        # to int
        page_index = int(page_index)
        objects = []

        for obj in page:
            if obj.tag in ["text", "frame"]:
                obj_data = {
                    "type": obj.tag,
                    "id": obj.get("id"),
                    "xmin": obj.get("xmin"),
                    "ymin": obj.get("ymin"),
                    "xmax": obj.get("xmax"),
                    "ymax": obj.get("ymax"),
                }
                objects.append(obj_data)

        page_objects[page_index] = objects

    return page_objects

# コマに内包されている吹き出しのバウンディングボックスを取得
# デフォルト閾値は0.5
def get_bounded_text(panel_info, text_info, iou_threshold=0.5):
    """
    吹き出しのバウンディングボックスのうち、パネルに内包されているものを取得
    :param panel_info: パネルのバウンディングボックス情報
    :param text_info: テキストのバウンディングボックス情報
    :param iou_threshold: IoUの閾値
    :return: パネルに内包されているテキストのバウンディングボックス情報
    """
    panel_xmin = int(panel_info["xmin"])
    panel_ymin = int(panel_info["ymin"])
    panel_xmax = int(panel_info["xmax"])
    panel_ymax = int(panel_info["ymax"])
    # print(f'panel_xmin: {panel_xmin}, panel_ymin: {panel_ymin}, panel_xmax: {panel_xmax}, panel_ymax: {panel_ymax}')

    bounded_text = []
    for text in text_info:
        text_xmin = int(text["xmin"])
        text_ymin = int(text["ymin"])
        text_xmax = int(text["xmax"])
        text_ymax = int(text["ymax"])
        # print(f'text_xmin: {text_xmin}, text_ymin: {text_ymin}, text_xmax: {text_xmax}, text_ymax: {text_ymax}')

        # 重なっている領域の座標を計算
        overlap_xmin = max(panel_xmin, text_xmin)
        overlap_ymin = max(panel_ymin, text_ymin)
        overlap_xmax = min(panel_xmax, text_xmax)
        overlap_ymax = min(panel_ymax, text_ymax)
        # print(f'overlap_xmin: {overlap_xmin}, overlap_ymin: {overlap_ymin}, overlap_xmax: {overlap_xmax}, overlap_ymax: {overlap_ymax}')

        # 重なっている領域の面積を計算
        overlap_area = max(0, overlap_xmax - overlap_xmin) * max(0, overlap_ymax - overlap_ymin)
        # print("overlap_area", overlap_area)

        # パネルとテキストのバウンディングボックスの面積を計算
        panel_area = (panel_xmax - panel_xmin) * (panel_ymax - panel_ymin)
        text_area = (text_xmax - text_xmin) * (text_ymax - text_ymin)
        # print(f'panel_area: {panel_area}, text_area: {text_area}')

        # IoUを計算
        iou = overlap_area / text_area
        print("iou", iou)

        # IoUがしきい値以上なら、テキストを追加
        if iou >= iou_threshold:
            bounded_text.append(text)

    return bounded_text




# 画像ファイル名をインデックスから取得
def index_to_img_path(index, img_folder_path):
    """
    indexから画像ファイル名を取得
    :param index: 画像のインデックス
    :param img_folder_path: 画像フォルダのパス
    :return: 画像ファイル名
    """
    img_path = img_folder_path + str(index).zfill(3) + ".jpg"
    return img_path


# バウンディングボックスを画像に描画
def draw_bbox(img, page_objects, output_path):
    """
    バウンディングボックスを画像に描画
    :param img: 画像
    :param page_objects: バウンディングボックス情報
    :param output_path: 出力画像のパス
    :return img: バウンディングボックスが描画された画像
    """
    colors = {
        "frame": (0, 255, 0),  # 緑
        "body": (255, 0, 0),  # 青
        "face": (0, 0, 255),  # 赤
        "text": (255, 255, 0),  # シアン
    }
    for obj in page_objects:
        obj_type = obj["type"]
        xmin = int(obj["xmin"])
        ymin = int(obj["ymin"])
        xmax = int(obj["xmax"])
        ymax = int(obj["ymax"])
        color = colors[obj_type]
        # バウンディングボックスの中心座標を計算
        center = (int((xmin + xmax) / 2), int((ymin + ymax) / 2))
        # print(f"type:{obj_type}, xmin:{xmin}, ymin:{ymin}, xmax:{xmax}, ymax:{ymax}, center:{center}")
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
    return img
    cv2.imshow("img", img)
    # cv2.imwrite(output_path, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def extractSpeechBalloon(img):
    """
    画像から輪郭検出して吹き出しを抽出
    :param img: 画像
    :return: 吹き出しのバウンディングボックス情報
    """
    speech_balloons = []
    if img is None:
        return None
    
    # 画像がカラーの場合はグレースケールに変換
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    # 画像の二値化
    binary = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)[1]
    gaussian_img = cv2.GaussianBlur(gray, (3, 3), 0)
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.erode(binary, kernel, (-1, -1), iterations=1)
    binary = cv2.dilate(binary, kernel, (-1, -1), iterations=1)
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    for contour in contours:
        # バウンディングボックスの座標を取得
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        length = cv2.arcLength(contour, True)
        en = 0.0
        if (
            gaussian_img.shape[0] * gaussian_img.shape[1] * 0.005 <= area
            and area < gaussian_img.shape[0] * gaussian_img.shape[1] * 0.05
        ):
            en = 4.0 * np.pi * area / (length * length)
        
        # 一定のサイズ以上の輪郭のみを吹き出しとみなす
        if en > 0.4:
            speech_bubble = {
                'type': 'text',
                'xmin': str(x),
                'ymin': str(y),
                'xmax': str(x + w),
                'ymax': str(y + h)
            }
            speech_balloons.append(speech_bubble)
    
    return speech_balloons


