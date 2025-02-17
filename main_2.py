from fastapi import FastAPI, Query
import httpx
import xml.etree.ElementTree as ET

app = FastAPI()

# Unipass API 기본 URL 및 고정된 crkyCn 값
BASE_URL = "https://unipass.customs.go.kr:38010/ext/rest/cargCsclPrgsInfoQry/retrieveCargCsclPrgsInfo"
CRKY_CN = "k260e285l002p153c060e060c1"

@app.get("/carg-info/")
async def get_carg_info(cargMtNo: str = Query(..., description="Cargo Manifest Number")):
    """
    cargMtNo를 입력받아 Unipass API에 요청을 보내고 응답을 XML로 파싱하여 반환하는 엔드포인트
    """
    params = {
        "crkyCn": CRKY_CN,
        "cargMtNo": cargMtNo
    }

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

            # XML 파싱 (Content-Type 검사 제거)
            root = ET.fromstring(response.text)

            # 필요한 데이터를 XML에서 추출 (예시)
            data = {}
            for elem in root.iter():
                data[elem.tag] = elem.text.strip() if elem.text else None

            return data  # JSON 형태로 반환

        except httpx.HTTPStatusError as e:
            return {"error": "HTTP Error", "details": str(e)}
        except httpx.RequestError as e:
            return {"error": "Request Error", "details": str(e)}
        except ET.ParseError as e:
            return {"error": "XML Parse Error", "details": str(e)}
