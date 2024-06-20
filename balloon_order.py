import math
import os
import cv2
from modules import *
import math
import numpy as np
import itertools
from scipy.spatial import distance_matrix

def get_distance(x1, y1, x2, y2):
    """
    2点間の距離を計算する
    :param x1: 点1のx座標
    :param y1: 点1のy座標
    :param x2: 点2のx座標
    :param y2: 点2のy座標
    :return: 2点間の距離
    """
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def find_nearest_balloon(panel, bounded_text):
    """
    コマ右上の座標と最も近い吹き出しを見つける
    :param panel: コマのバウンディングボックス情報
    :param bounded_text: コマ内の吹き出しのバウンディングボックス情報
    :return: 最も近い吹き出しのバウンディングボックス情報
    :see also: get_distance 2点間の距離を計算する関数
    """
    if not bounded_text:
        return None
    
    panel_xmax, panel_ymin = int(panel['xmax']), int(panel['ymin'])
    min_dist = float('inf')
    nearest_balloon = None
    
    for balloon in bounded_text:
        try:
            balloon_x = (int(balloon['xmin']) + int(balloon['xmax'])) / 2
            balloon_y = (int(balloon['ymin']) + int(balloon['ymax'])) / 2
            dist = get_distance(panel_xmax, panel_ymin, balloon_x, balloon_y)
            print("dist", dist)
            if dist < min_dist:
                min_dist = dist
                nearest_balloon = balloon
        except (ValueError, TypeError):
            continue
    
    return nearest_balloon


def order_balloons(panel, bounded_text):
    """
    吹き出しの順番を決定する
    :param panel: コマのバウンディングボックス情報
    :param bounded_text: コマ内の吹き出しのバウンディングボックス情報
    :return: 吹き出しの順番のリスト
    :see also: find_nearest_balloon コマ右上の座標と最も近い吹き出しを見つける関数
    :see also: get_distance 2点間の距離を計算する関数
    """
    panel_xmin, panel_ymin = int(panel['xmin']), int(panel['ymin'])
    start = find_nearest_balloon(panel, bounded_text)
    
    if start is None:
        # bounded_textが空の場合など、適切に処理する
        return []

    start_xmin, start_ymin = int(start['xmin']), int(start['ymin'])
    start_xmax, start_ymax = int(start['xmax']), int(start['ymax'])
    start_x, start_y = (start_xmin + start_xmax) / 2, (start_ymin + start_ymax) / 2
    ordered_balloons = [start]
    unordered_balloons = [b for b in bounded_text if b != start]
    
    while unordered_balloons:
        min_dist = float('inf')
        nearest_balloon = None
        
        for balloon in unordered_balloons:
            balloon_xmin, balloon_ymin = int(balloon['xmin']), int(balloon['ymin'])
            balloon_xmax, balloon_ymax = int(balloon['xmax']), int(balloon['ymax'])
            balloon_x, balloon_y = (balloon_xmin + balloon_xmax) / 2, (balloon_ymin + balloon_ymax) / 2
            dist = get_distance(start_x, start_y, balloon_x, balloon_y) + get_distance(balloon_x, balloon_y, panel_xmin, panel_ymin)
            if dist < min_dist:
                min_dist = dist
                nearest_balloon = balloon
        
        ordered_balloons.append(nearest_balloon)
        unordered_balloons.remove(nearest_balloon)
        start_xmin, start_ymin = int(nearest_balloon['xmin']), int(nearest_balloon['ymin'])
        start_xmax, start_ymax = int(nearest_balloon['xmax']), int(nearest_balloon['ymax'])
        start_x, start_y = (start_xmin + start_xmax) / 2, (start_ymin + start_ymax) / 2
    
    return ordered_balloons

# こちらを採用
def order_balloons2(panel, bounded_text):
    """
    吹き出しの順番を決定する(全順序)
    :param panel: コマのバウンディングボックス情報
    :param bounded_text: コマ内の吹き出しのバウンディングボックス情報
    :return: 吹き出しの順番のリスト
    :see also: find_nearest_balloon コマ右上の座標と最も近い吹き出しを見つける関数
    :see also: get_distance 2点間の距離を計算する関数
    """
    panel_xmax, panel_ymin = int(panel['xmax']), int(panel['ymin'])
    start = find_nearest_balloon(panel, bounded_text)
    if start is None:
        return []
    
    start_point = [(int(start['xmin']) + int(start['xmax'])) / 2, (int(start['ymin']) + int(start['ymax'])) / 2]
    end_point = [int(panel['xmin']), int(panel['ymax'])]
    
    # 吹き出しの中心座標を取得
    points = []
    for balloon in bounded_text:
        center = [(int(balloon['xmin']) + int(balloon['xmax'])) / 2, (int(balloon['ymin']) + int(balloon['ymax'])) / 2]
        points.append(center)
        # スタート地点は除外
        if center == start_point:
            points.remove(center)
    # 始点をstart_point,終点ををend_pointとして，pointsを全て通る最短経路を求める
    points = [start_point] + points + [end_point]
    print(f'points: {points}')
    # 各点間の距離を計算
    dist_matrix = distance_matrix(points, points)
    
    # 巡回経路となるインデックスを全列挙
    N = len(points)
    indices = np.arange(N)
    paths = [p for p in itertools.permutations(indices[1:-1])]
    
    # 各巡回経路の総距離を計算し、最短経路を求める
    best_dist = np.inf
    best_path = None
    for path in paths:
        path = [0] + list(path) + [N-1]
        dist = np.sum([dist_matrix[path[i], path[i+1]] for i in range(len(path)-1)])
        if dist < best_dist:
            best_dist = dist
            best_path = path
            
    # 最短経路上の吹き出しをbounded_textから取得
    ordered_balloons = []
    for i in best_path[0:-1]:
        point = points[i]
        for balloon in bounded_text:
            balloon_center = [(int(balloon['xmin']) + int(balloon['xmax'])) / 2, (int(balloon['ymin']) + int(balloon['ymax'])) / 2]
            print(f'point: {point}, balloon_center: {balloon_center}')
            if balloon_center == point:
                ordered_balloons.append(balloon)
            else:
                print("not found")
                
                
    return ordered_balloons




if __name__ == '__main__':
    # パスの設定
    manga109_ano_dir = "./../Manga109_released_2021_12_30/annotations.v2020.12.18/"  # アノテーションファイルのディレクトリ
    manga109_img_dir = "./../Manga109_released_2021_12_30/images/"  # 画像ファイルのディレクトリ
    files = os.listdir(manga109_ano_dir)  # アノテーションファイルのリスト
    img_folders = os.listdir(manga109_img_dir)  # 画像フォルダのリスト

    # マンガのタイトルを指定
    manga_title = "Belmondo"
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

            img = cv2.imread(img_path)

            # 吹き出しの検出
            speech_balloons = extractSpeechBalloon(img)

            # コマ内の吹き出しを取得
            # 入力をmanga109にする場合
            bounded_text = get_bounded_text(panel, balloons[page_index])
            # 入力を画像処理による吹き出し検出結果にする場合
            # bounded_text = get_bounded_text(panel, speech_balloons)
            print("bounded_text", bounded_text)

            # print("speech_balloons", speech_balloons)
            # draw_img = draw_bbox(img,speech_balloons, "output.jpg")
            draw_img = draw_bbox(img, [panel], (0, 255, 0))
            # draw_img = draw_bbox(draw_img, bounded_text, (0, 0, 255))
            cv2.imshow("img", draw_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            ordered_balloons = order_balloons2(panel, bounded_text)
            drawimg = draw_bbox(img, [panel], "output.jpg")
            for balloon in ordered_balloons:
                drawimg = draw_bbox(drawimg, [balloon], "output.jpg")
                cv2.imshow("img", drawimg)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            print("ordered_balloons", ordered_balloons)