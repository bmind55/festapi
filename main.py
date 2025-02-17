from fastapi import FastAPI, Query
import httpx
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

app = FastAPI()

BASE_URL = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo"
CRKY_CN = "k260e285l002p153c060e060c1"

# ✅ XML을 자동으로 중첩된 JSON으로 변환하는 재귀 함수
def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    result = {}
    
    # 각 하위 요소 순회
    for child in element:
        child_data = xml_to_dict(child) if len(child) > 0 else (child.text.strip() if child.text else None)
        
        # 동일한 태그가 여러 개 있을 경우 리스트로 변환
        if child.tag in result:
            if isinstance(result[child.tag], list):
                result[child.tag].append(child_data)
            else:
                result[child.tag] = [result[child.tag], child_data]
        else:
            result[child.tag] = child_data
    
    return result

@app.get("/carg-info/")
async def get_carg_info(
    cargMtNo: Optional[str] = Query(None, description="Cargo Manifest Number"),
    mblNo: Optional[str] = Query(None, description="Master B/L Number"),
    hblNo: Optional[str] = Query(None, description="House B/L Number"),
    blYy: Optional[str] = Query(None, description="B/L Year")
) -> Dict[str, Any]:
    """
    cargMtNo 또는 (mblNo + blYy) 또는 (hblNo + blYy)를 입력받아 Unipass API에 요청하고
    XML 데이터를 자동 변환하여 JSON으로 반환
    """
    if not cargMtNo and not (mblNo and blYy) and not (hblNo and blYy):
        return {"error": "Invalid parameters", "details": "You must provide either cargMtNo, or (mblNo + blYy), or (hblNo + blYy)."}

    params = {"crkyCn": CRKY_CN}
    if cargMtNo:
        params["cargMtNo"] = cargMtNo
    elif mblNo and blYy:
        params["mblNo"] = mblNo
        params["blYy"] = blYy
    elif hblNo and blYy:
        params["hblNo"] = hblNo
        params["blYy"] = blYy

    async with httpx.AsyncClient(verify=False) as client:
        async with client.stream("GET", BASE_URL, params=params) as response:
            response.raise_for_status()
            raw_data = await response.aread()

            # 원본 XML 데이터를 저장 (디버깅용)
            with open("unipass_raw_response.xml", "wb") as f:
                f.write(raw_data)

            # XML을 자동으로 중첩 JSON으로 변환
            root = ET.fromstring(raw_data.decode("utf-8"))
            data = xml_to_dict(root)

            return data
