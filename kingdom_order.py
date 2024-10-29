import itertools
import json
import cv2
from scipy.spatial import distance_matrix
import math
import numpy as np
from modules import *

def get_distance(x1, y1, x2, y2):
    """
    2点間の距離を計算する
    :param x1: 点1のx座標
    :param y1: 点1のy座標
    :param x2: 点2のx座標
    :param y2: 点2のy座標
    :return: 2点間の距離
    """
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


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

    panel_xmax, panel_ymin = int(panel["xmax"]), int(panel["ymin"])
    min_dist = float("inf")
    nearest_balloon = None

    for balloon in bounded_text:
        try:
            balloon_x = (int(balloon["xmin"]) + int(balloon["xmax"])) / 2
            balloon_y = (int(balloon["ymin"]) + int(balloon["ymax"])) / 2
            dist = get_distance(panel_xmax, panel_ymin, balloon_x, balloon_y)
            # print("dist", dist)
            if dist < min_dist:
                min_dist = dist
                nearest_balloon = balloon
        except (ValueError, TypeError):
            continue

    return nearest_balloon

def order_balloons2(panel, bounded_text):
    """
    吹き出しの順番を決定する(全順序)
    :param panel: コマのバウンディングボックス情報
    :param bounded_text: コマ内の吹き出しのバウンディングボックス情報
    :return: 吹き出しの順番のリスト
    :see also: find_nearest_balloon コマ右上の座標と最も近い吹き出しを見つける関数
    :see also: get_distance 2点間の距離を計算する関数
    """
    panel_xmax, panel_ymin = int(panel["xmax"]), int(panel["ymin"])
    start = find_nearest_balloon(panel, bounded_text)
    if start is None:
        return []

    start_point = [(int(start["xmin"]) + int(start["xmax"])) / 2, (int(start["ymin"]) + int(start["ymax"])) / 2]
    end_point = [int(panel["xmin"]), int(panel["ymax"])]

    # 吹き出しの中心座標を取得
    points = []
    for balloon in bounded_text:
        center = [(int(balloon["xmin"]) + int(balloon["xmax"])) / 2, (int(balloon["ymin"]) + int(balloon["ymax"])) / 2]
        points.append(center)
        # スタート地点は除外
        if center == start_point:
            points.remove(center)
    # 始点をstart_point,終点ををend_pointとして，pointsを全て通る最短経路を求める
    points = [start_point] + points + [end_point]
    # print(f'points: {points}')
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
        path = [0] + list(path) + [N - 1]
        dist = np.sum([dist_matrix[path[i], path[i + 1]] for i in range(len(path) - 1)])
        if dist < best_dist:
            best_dist = dist
            best_path = path

    # 最短経路上の吹き出しをbounded_textから取得
    ordered_balloons = []
    for i in best_path[0:-1]:
        point = points[i]
        for balloon in bounded_text:
            balloon_center = [
                (int(balloon["xmin"]) + int(balloon["xmax"])) / 2,
                (int(balloon["ymin"]) + int(balloon["ymax"])) / 2,
            ]
            # print(f'point: {point}, balloon_center: {balloon_center}')
            if balloon_center == point:
                ordered_balloons.append(balloon)
            else:
                print("not found")

    return ordered_balloons

def order_objs(obj_data_list, frame_list):
    """
    コマ内のオブジェクトの順番を決定する(全順序)
    :param obj_data_list: コマ内のオブジェクトのバウンディングボックス情報
    :param frame_list: コマ内のフレームのバウンディングボックス情報
    :return: オブジェクトの順番のリスト
    """
    pseudo_regions = []
    for i, frame in enumerate(frame_list):
        overlaps = []
        for j, other_frame in enumerate(frame_list):
            if i != j:
                # 重なりを計算
                overlap_xmin = max(frame["xmin"], other_frame["xmin"])
                overlap_ymin = max(frame["ymin"], other_frame["ymin"])
                overlap_xmax = min(frame["xmax"], other_frame["xmax"])
                overlap_ymax = min(frame["ymax"], other_frame["ymax"])

                if overlap_xmax > overlap_xmin and overlap_ymax > overlap_ymin:
                    overlaps.append([overlap_xmin, overlap_ymin, overlap_xmax, overlap_ymax])

        if overlaps:
            # 重なりがある場合、擬似的なコマ領域を計算
            overlap = np.array(overlaps).mean(axis=0)
            mid_x = (overlap[0] + overlap[2]) / 2
            pseudo_regions.append([frame["xmin"], frame["ymin"], mid_x, frame["ymax"]])
        else:
            pseudo_regions.append([frame["xmin"], frame["ymin"], frame["xmax"], frame["ymax"]])

    return np.array(pseudo_regions)


if __name__ == "__main__":
    # パスの設定
    img_path = "./../キングダム/17/17.png"
    ano_path = "./../キングダム/17/17.json"
    
    obj_data_list = []
    frame_list = []
    
    with open(ano_path, "r") as f:
        data = json.load(f)
        for obj in data["shapes"]:
            obj_data = {}
            obj_data["label"] = obj["label"]
            obj_data["xmin"] = min(int(obj["points"][0][0]), int(obj["points"][1][0]))
            obj_data["ymin"] = min(int(obj["points"][0][1]), int(obj["points"][1][1]))
            obj_data["xmax"] = max(int(obj["points"][0][0]), int(obj["points"][1][0]))
            obj_data["ymax"] = max(int(obj["points"][0][1]), int(obj["points"][1][1]))
            if obj["label"] == "frame":
                frame_list.append(obj_data)
            else:
                obj_data_list.append(obj_data)
    
    img = cv2.imread(img_path)
    
    for frame in frame_list:
        cv2.rectangle(img, (frame["xmin"], frame["ymin"]), (frame["xmax"], frame["ymax"]), (0, 255, 0), 2)
        bounded_objs = get_bouded_obj(frame, obj_data_list)
        ordered_objs = order_balloons2(frame, bounded_objs)
        print(ordered_objs)
        # for obj in bounded_objs:
        #     cv2.rectangle(img, (obj["xmin"], obj["ymin"]), (obj["xmax"], obj["ymax"]), (0, 0, 255), 2)
        #     cv2.putText(img, obj["label"], (obj["xmin"], obj["ymin"]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        for obj in ordered_objs:
            cv2.rectangle(img, (obj["xmin"], obj["ymin"]), (obj["xmax"], obj["ymax"]), (0, 0, 255), 2)
            cv2.putText(img, obj["label"], (obj["xmin"], obj["ymin"]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow("img", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()