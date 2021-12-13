import json

if __name__ == '__main__':
    import os
    base_path = 'saved/model/cloud_ranger_runner/sock_shop/alpha_0_15/score_ranking_list/'
    for file in os.listdir(base_path):
        if file.endswith("json"):
            with open((os.path.abspath(base_path + file))) as f:
                for k, v in json.load(f).items():
                    if len(v) == 0:
                        print(k)
