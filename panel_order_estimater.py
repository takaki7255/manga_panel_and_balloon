from modules import *
import cv2
import os
import numpy as np


def calculate_pseudo_regions(panels):
    # バウンディングボックスを数値に変換
    boxes = np.array([[int(p["xmin"]), int(p["ymin"]), int(p["xmax"]), int(p["ymax"])] for p in panels])

    pseudo_regions = []
    for i, box in enumerate(boxes):
        overlaps = []
        for j, other_box in enumerate(boxes):
            if i != j:
                # 重なりを計算
                overlap_xmin = max(box[0], other_box[0])
                overlap_ymin = max(box[1], other_box[1])
                overlap_xmax = min(box[2], other_box[2])
                overlap_ymax = min(box[3], other_box[3])

                if overlap_xmax > overlap_xmin and overlap_ymax > overlap_ymin:
                    overlaps.append([overlap_xmin, overlap_ymin, overlap_xmax, overlap_ymax])

        if overlaps:
            # 重なりがある場合、擬似的なコマ領域を計算
            overlap = np.array(overlaps).mean(axis=0)
            mid_x = (overlap[0] + overlap[2]) / 2
            pseudo_regions.append([box[0], box[1], mid_x, box[3]])
        else:
            pseudo_regions.append(box)

    return np.array(pseudo_regions)


def order_panels(pseudo_regions, page_width, page_height):
    ordered = []
    remaining = list(range(len(pseudo_regions)))

    while remaining:
        # 上側に未定義のコマがないものを探す
        top_candidates = [
            i for i in remaining if all(pseudo_regions[i][1] <= pseudo_regions[j][3] for j in remaining if i != j)
        ]

        if not top_candidates:
            break  # エラー処理が必要かもしれません

        # 右上座標がページ右上に最も近いコマを選択
        closest = min(
            top_candidates, key=lambda i: ((page_width - pseudo_regions[i][2]) ** 2 + pseudo_regions[i][1] ** 2) ** 0.5
        )

        ordered.append(closest)
        remaining.remove(closest)

        current_region = pseudo_regions[closest]

        # 左端かどうかをチェック
        if any(pseudo_regions[i][2] < current_region[0] for i in remaining):
            # 左端でない場合、次のコマを探す
            next_candidates = [
                i
                for i in remaining
                if pseudo_regions[i][1] >= current_region[3] and pseudo_regions[i][0] >= current_region[2]
            ]
            if next_candidates:
                next_panel = min(
                    next_candidates,
                    key=lambda i: (
                        (pseudo_regions[i][0] - current_region[2]) ** 2
                        + (pseudo_regions[i][1] - current_region[3]) ** 2
                    )
                    ** 0.5,
                )
                ordered.append(next_panel)
                remaining.remove(next_panel)

    return ordered


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
        print("panels", panels[page_index])
