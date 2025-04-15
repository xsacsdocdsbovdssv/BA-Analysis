import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report

# 加载数据
df = pd.read_csv("test2.csv")  # 600条已标注的形容词数据（含类别）
with open("sense_embeddings.pkl", "rb") as f:
    sense_embeds = pickle.load(f)

# 过滤掉没有embedding的词
df = df[df["word"].isin(sense_embeds.keys())].reset_index(drop=True)

# 构造特征和标签
X = np.stack([sense_embeds[word] for word in df["word"]])
y = df["label"]  # 假设label列是语义类别

# 编码标签
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 划分训练集和验证集
X_train, X_val, y_train, y_val = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# 训练模型
model = XGBClassifier(use_label_encoder=False, eval_metric="mlogloss")
model.fit(X_train, y_train)

# 验证性能
y_pred = model.predict(X_val)
print(classification_report(y_val, y_pred, target_names=le.classes_))

# 保存模型和标签编码器
with open("xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)


# 加载未标注数据
test_df = pd.read_csv("test1.csv")  # 含1800多条形容词
with open("sense_embeddings.pkl", "rb") as f:
    sense_embeds = pickle.load(f)

# 加载模型与标签编码器
with open("xgb_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

# 构建预测样本（test1中未在test2中出现的）
test_df = test_df[~test_df["word"].isin(pd.read_csv("test2.csv")["word"])].reset_index(drop=True)
test_df = test_df[test_df["word"].isin(sense_embeds.keys())].reset_index(drop=True)

X_test = np.stack([sense_embeds[word] for word in test_df["word"]])
y_pred = model.predict(X_test)
labels_pred = le.inverse_transform(y_pred)

# 保存结果
test_df["predicted_label"] = labels_pred
test_df.to_csv("test1_predicted.csv", index=False)
print("✅ 已保存预测结果到 test1_predicted.csv")
