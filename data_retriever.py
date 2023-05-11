def txt2list(file_path):
  with open(file_path, 'r') as f:
    return [line.strip() for line in f.readlines()]
  