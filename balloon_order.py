import math
import os
import cv2
from modules import *

def get_bubble_order(panel_coords, bubble_coords):
    """
    panel_coords: コマの座標 (x1, y1, x2, y2)
    bubble_coords: 吹き出しの座標のリスト [(x1, y1, x2, y2), ...]
    return: 吹き出しの順序のリスト
    """
    # 1. 吹き出しの中心座標を計算
    bubble_centers = [(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2) for x1, y1, x2, y2 in bubble_coords]
    
    # 2. コマの右上の座標を取得
    panel_x2, panel_y1 = panel_coords[2], panel_coords[1]
    
    # 3. 始点の吹き出しを決定
    start_bubble = min(bubble_centers, key=lambda c: math.hypot(c[0] - panel_x2, c[1] - panel_y1))
    start_index = bubble_centers.index(start_bubble)
    
    # 4. 最短経路を求める (ここではDijkstraのアルゴリズムを使用)
    # 経路は吹き出しの中心座標を通る
    path = dijkstra(bubble_centers, start_index, (panel_coords[0], panel_coords[3]))
    
    # 5. 経路の順序で吹き出しに番号を付ける
    bubble_order = [bubble_centers.index(coord) for coord in path]
    
    return bubble_order

def dijkstra(coords, start_index, goal):
    """
    coords: 吹き出しの中心座標のリスト
    start_index: 始点のインデックス
    goal: ゴールの座標 (x, y)
    return: 最短経路の座標のリスト
    """
    # 1. 各頂点までの最短距離を保存するリスト
    dist = [math.inf] * len(coords)
    dist[start_index] = 0
    
    # 2. 各頂点までの最短距離の経路を保存するリスト
    prev = [None] * len(coords)
    
    # 3. 未確定の頂点の集合
    Q = set(range(len(coords)))
    
    # 4. メインのループ
    while Q:
        # 未確定の頂点のうち、最も距離が小さい頂点を取り出す
        u = min(Q, key=lambda v: dist[v])
        Q.remove(u)
        
        # ゴールに到達したら終了
        if coords[u] == goal:
            break
        
        # 隣接する頂点を更新
        for v in Q:
            alt = dist[u] + math.hypot(coords[u][0] - coords[v][0], coords[u][1] - coords[v][1])
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
    
    # 5. 経路を復元
    path = []
    u = coords.index(goal)
    while prev[u] is not None:
        path.append(coords[u])
        u = prev[u]
    path.append(coords[u])
    
    return path[::-1]

if __name__ == '__main__':
    # パスの設定
    manga109_ano_dir = "./../Manga109_released_2021_12_30/annotations.v2020.12.18/"  # アノテーションファイルのディレクトリ
    manga109_img_dir = "./../Manga109_released_2021_12_30/images/"  # 画像ファイルのディレクトリ
    files = os.listdir(manga109_ano_dir)  # アノテーションファイルのリスト
    img_folders = os.listdir(manga109_img_dir)  # 画像フォルダのリスト

    # マンガのタイトルを指定
    manga_title = "ARMS"
    ano_file_path = manga109_ano_dir + manga_title + ".xml"
    img_folder_path = manga109_img_dir + manga_title + "/"

    # 画像ファイル名を取得
    imgs = os.listdir(img_folder_path)
    imgs.sort()
    panels = get_panelbbox_info_from_xml(ano_file_path)
    balloons = get_textbbox_info_from_xml(ano_file_path)
    for page_index in balloons.keys():
        img_path = index_to_img_path(page_index, img_folder_path)
        print("img_path", img_path)
        for panel in panels[page_index]:
            print("panel", panel)
            print("balloons", balloons[page_index])
            bounded_text = get_bounded_text(panel, balloons[page_index])
            print("bounded_text", bounded_text)
    # panel_coords = (0, 0, 10, 10)
    # bubble_coords = [(1, 1, 3, 3), (2, 2, 4, 4), (3, 3, 5, 5), (4, 4, 6, 6), (5, 5, 7, 7)]
    # print(get_bubble_order(panel_coords, bubble_coords))  # => [0, 1, 2, 3, 4]