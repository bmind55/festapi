from fastapi import FastAPI, Query
import httpx
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

app = FastAPI()

BASE_URL = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo"
CRKY_CN = "k260e285l002p153c060e060c1"

@app.get("/carg-info/")
async def get_carg_info(
    cargMtNo: Optional[str] = Query(None, description="Cargo Manifest Number"),
    mblNo: Optional[str] = Query(None, description="Master B/L Number"),
    hblNo: Optional[str] = Query(None, description="House B/L Number"),
    blYy: Optional[str] = Query(None, description="B/L Year")
) -> Dict:
    """
    cargMtNo 또는 (mblNo + blYy) 또는 (hblNo + blYy)를 입력받아 Unipass API에 요청을 보내고 응답을 JSON으로 반환하는 엔드포인트
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

            root = ET.fromstring(raw_data.decode("utf-8"))

            # 다건 데이터 처리
            cargo_list = []
            for cargo in root.findall("cargCsclPrgsInfoQryVo"):
                cargo_data = {elem.tag: elem.text.strip() if elem.text else None for elem in cargo}
                cargo_list.append(cargo_data)

            # 단건 데이터 처리
            data = {elem.tag: elem.text.strip() if elem.text else None for elem in root if elem.tag != "cargCsclPrgsInfoQryVo"}
            data["cargo_list"] = cargo_list  # 다건 데이터를 리스트로 추가

            return data
