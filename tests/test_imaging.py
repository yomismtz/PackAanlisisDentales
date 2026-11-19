import numpy as np
from app.imaging import adjust, rectify

def test_adjust_returns_copy():
    source=np.full((80,100,3),100,dtype=np.uint8)
    result=adjust(source,brightness=20,contrast=100,sharpness=100)
    assert result is not source
    assert source.mean()==100
    assert result.mean()>source.mean()

def test_rectify_four_corners():
    image=np.zeros((160,200,3),dtype=np.uint8)
    result=rectify(image,[(10,10),(180,15),(175,140),(15,145)])
    assert result.shape[0]>100
    assert result.shape[1]>150
