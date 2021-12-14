from runner.cloud_ranger_runner import CloudRangerRunner
import datetime
import os
import json
import gc


# Update config
def update_config(start_index, batch_size):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = base_dir + '/data/sock-shop/metric/'
    file_list = []
    for file in os.listdir(path):
        if file.endswith('.csv'):
            file_list.append(file[:-4])
    file_list.sort()
    with open(base_dir + '/data/sock-shop/label.json', 'w+') as f:
        data = {}
        for i in range(start_index, min(start_index + batch_size, len(file_list))):
            data[file_list[i]] = "0"
        json.dump(data, f)
    with open(base_dir + '/config/data_rca_model_name_sock-shop.json', 'w+') as f:
        data = {"train": [], "valid": [], "test": [], "data_type": {"metric": True, "tracing": False, "logging": False}}
        lst = [file_list[i] for i in range(start_index, min(start_index + batch_size, len(file_list)))]
        data["test"] = lst
        data["train"] = lst
        json.dump(data, f)


# Run
if __name__ == '__main__':
    for i in [0, 60, 120, 180, 240]:
        update_config(i, 60)
        print('start:', datetime.datetime.now())
        cloud_ranger_runner = CloudRangerRunner()
        cloud_ranger_runner.run()
        cloud_ranger_runner.test()
        print('finished:', datetime.datetime.now())
        del cloud_ranger_runner
        gc.collect()


