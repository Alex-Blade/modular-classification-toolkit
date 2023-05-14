import os
import torch
import numpy as np

from torch.utils.data import Dataset
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
import joblib
from pathlib import Path

from .model import Model


__all__ = ["SVM"]


class LabeledDataset(Dataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.unique_classes = None
        self.category_map = None

    def __len__(self):
        len(os.listdir(self.root_dir))

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        fld = Path(self.root_dir, f"b{idx}")
        tiffs = []
        classes = []
        for file in fld.iterdir():
            cls_name = file.name.split('_')[0]
            data = np.load(file)
            bands = [data[arr].flatten() for arr in data.files]
            data.close()
            stacked_bands = np.dstack(bands)[0]
            tiffs.append(stacked_bands[~np.all(stacked_bands == 0, axis=1)])
            for _ in range(tiffs[-1].shape[0]):
                classes.append(cls_name)
        if (self.category_map is None) or (self.unique_classes is None):
            self.unique_classes = set(classes)
            self.category_map = {k: idx for idx, k in enumerate(self.unique_classes)}
        labels = [self.category_map[_] for _ in classes]

        return np.concatenate(tiffs), np.asarray(labels)


class UnlabeledDataset(Dataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __len__(self) -> int:
        return len(os.listdir(self.root_dir))

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        fld = Path(self.root_dir, f"b{idx}")
        tiffs_and_paths = []
        for file in fld.iterdir():
            data = np.load(file)
            bands = [data[arr].flatten() for arr in data.files]
            data.close()
            tiffs_and_paths.append((np.dstack(bands)[0], file))

        return tiffs_and_paths


class SVM(Model):
    _display_name = "SVM"

    def __init__(self):
        super().__init__()
        self.clf = None
        self.dataset = None
        self.class_map = {}

    def fit_unlabeled(self, data: str):
        raise NotImplementedError("SVM cannot be trained with unlabeled data")

    def fit_labeled(self, data: str):
        dataset = LabeledDataset(data)
        x, y = dataset[0]
        self.class_map = {v: k for k, v in dataset.category_map.items()}
        self.clf = make_pipeline(StandardScaler(), SGDClassifier(max_iter=1000, tol=1e-3))
        self.clf.fit(x, y)

    def save(self, file_name: str):
        joblib.dump({"model": self.clf, "class_map": self.class_map}, file_name)

    def load(self, file_name: str):
        dct = joblib.load(file_name)
        self.clf = dct["model"]
        self.class_map = dct["class_map"]

    def predict(self, data: str, output_folder: str):
        dataset = UnlabeledDataset(data)
        for i in range(len(dataset)):
            x, file = dataset[i][0]
            file = Path(output_folder, ("pred_" + file.name))
            res = self.clf.predict(x)
            res = np.array([self.class_map[i] for i in res])
            # sort_idx = np.argsort(transdict.keys())
            # idx = np.searchsorted(transdict.keys(), abc_array, sorter=sort_idx)
            # out = np.asarray(transdict.values())[sort_idx][idx]
            np.savez_compressed(file, res)
