# Config parser
This is a minimalist implementation of a configuration parser inspired by Hydra. I've come to notice that in real projects configuration management is very important and this project was a way to understand how some tools for configuration management work behind the scenes. 
This configuration parser allows to overwrite a YAML from the CLI while supporting group configurations (see examples below). 
It works as follows:
1. Create a list of `(key, value)` pairs based the YAML and the CLI entries. CLI entries (i.e. overwrites) are appended at the end.
2. Iterate over the list while keeping the _last_ value for each `(key, value)` pair.

**Examples**

```bash
python3 parse.py --config_filename training.yaml -optimizer=best
```

```diff
  batch_size: 256
  dataset_id: imagenet_1k
  epochs: 90
  model_name: resnet50
  optimizer:
-   lr: 0.1
-   name: sgd
-   weight_decay: 0.0001
+   lr: 0.5
+   name: adam
+   weight_decay: 0.001
  val_size: 0.3
```
We changed _all_ the configurations from the optimizer with `-optimizer=best`. The group options were read from `optimizer/best.yaml`. 

```bash
python3 parse.py --config_filename training.yaml -optimizer.lr=10
```

```diff
  batch_size: 256
  dataset_id: imagenet_1k
  epochs: 90
  model_name: resnet50
  optimizer:
-   lr: 0.1
+   lr: 10.0
    name: sgd
    weight_decay: 0.0001
  val_size: 0.3
```
Dotted keys let you override a single nested value without swapping the whole group. We changed only the learning from the optimizer with `-optimizer.lr=10`

```bash
python3 parse.py --config_filename training.yaml -dataset_id=imagenet_20k
```

```diff
batch_size: 256
- dataset_id: imagenet_1k
+ dataset_id: imagenet_20k
epochs: 90.0
model_name: resnet50
optimizer:
  lr: 0.1
  name: sgd
  weight_decay: 0.0001
val_size: 0.3
```
And you can of course change values that are not nested inside a group with the same notation.
