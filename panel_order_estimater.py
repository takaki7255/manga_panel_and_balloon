from modules import *
import cv2
import os
import numpy as np


def panel_order_estimater():
    """
    コマの順序を推定する
    """
    pass


if __name__ == "__main__":
    # パスの設定
    manga109_ano_dir = (
        "./../Manga109_released_2021_12_30/annotations.v2020.12.18/"  # アノテーションファイルのディレクトリ
    )
    manga109_img_dir = "./../Manga109_released_2021_12_30/images/"  # 画像ファイルのディレクトリ
    files = os.listdir(manga109_ano_dir)  # アノテーションファイルのリスト
    img_folders = os.listdir(manga109_img_dir)  # 画像フォルダのリスト

    # マンガのタイトルを指定
    manga_title = "PrismHeart"
    # 実験時，画像を指定する場合
    # sitei = "005"
    # 実験時，manga109を指定する場合True, 画像処理による抽出を指定する場合False
    manga109 = True
    # manga109 = False
    ano_file_path = manga109_ano_dir + manga_title + ".xml"
    img_folder_path = manga109_img_dir + manga_title + "/"

    # 画像ファイル名を取得
    imgs = os.listdir(img_folder_path)
    imgs.sort()

    panels = get_panelbbox_info_from_xml(ano_file_path)
    for page_index in panels.keys():
        img_path = index_to_img_path(page_index, img_folder_path)
        print("img_path", img_path)
    panel_order_estimater()
