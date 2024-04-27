classes = []
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

for i, class_name in enumerate(classes):
    print(f"{i}: {class_name}")
    