"""Pure geometry for hover-to-date chart tooltips."""
def nearest_point(series,x,width,left,right,threshold=22):
    if not series or width<=left+right:return None
    n=len(series)
    if n==1:return series[0] if abs(x-left)<=threshold else None
    span=width-left-right
    idx=round((x-left)*(n-1)/span)
    if not 0<=idx<n:return None
    expected=left+span*idx/(n-1)
    return series[idx] if abs(x-expected)<=threshold else None
