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

def test_adjust_preserves_transparency_channel():
    source=np.zeros((40,50,4),dtype=np.uint8)
    source[:,:,:3]=100
    source[:,:,3]=np.where(np.indices((40,50))[1] < 25, 0, 255)
    adjusted=adjust(source,brightness=20,contrast=110,sharpness=120)
    assert adjusted.shape[2]==4
    assert np.array_equal(adjusted[:,:,3],source[:,:,3])
