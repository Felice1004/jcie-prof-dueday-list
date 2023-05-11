def get_paper_status(file_path):
  with open(file_path, 'r') as f:
    paper_status = [line.strip() for line in f.readlines()]
    return paper_status
