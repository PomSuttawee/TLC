def union(rect_1: tuple, rect_2: tuple) -> tuple:
  x = min(rect_1[0], rect_2[0])
  y = min(rect_1[1], rect_2[1])
  w = max(rect_1[0]+rect_1[2], rect_2[0]+rect_2[2]) - x
  h = max(rect_1[1]+rect_1[3], rect_2[1]+rect_2[3]) - y
  return (x, y, w, h)

def intersection(rect_1: tuple, rect_2: tuple) -> tuple:
  x = max(rect_1[0], rect_2[0])
  y = max(rect_1[1], rect_2[1])
  w = min(rect_1[0]+rect_1[2], rect_2[0]+rect_2[2]) - x
  h = min(rect_1[1]+rect_1[3], rect_2[1]+rect_2[3]) - y
  if w<0 or h<0: return (0, 0, 0, 0)
  return (x, y, w, h)

def groupBoundingBox(rect_list: list) -> list:
  is_tested = [False for i in range(len(rect_list))]
  final_rect = []
  i = 0

  while i < len(rect_list):
    if not is_tested[i]:
      j = i+1
      while j <len(rect_list):
        if not is_tested[j] and intersection(rect_list[i], rect_list[j]) != (0, 0, 0, 0):
          rect_list[i] = union(rect_list[i], rect_list[j])
          is_tested[j] = True
          j = i
        j += 1
      final_rect += [rect_list[i]]
    i += 1
  return final_rect