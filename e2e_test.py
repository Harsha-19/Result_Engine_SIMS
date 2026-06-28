import asyncio
from playwright.async_api import async_playwright
import json
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        logs = {
            "console": [],
            "network": [],
            "api_responses": {}
        }

        page.on("console", lambda msg: logs["console"].append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda err: logs["console"].append({"type": "error", "text": str(err)}))

        async def handle_request(request):
            logs["network"].append({
                "type": "request",
                "url": request.url,
                "method": request.method
            })

        async def handle_response(response):
            logs["network"].append({
                "type": "response",
                "url": response.url,
                "status": response.status,
            })
            if "5000" in response.url:
                try:
                    body = await response.json()
                    logs["api_responses"][response.url] = body
                except:
                    pass

        page.on("request", handle_request)
        page.on("response", handle_response)

        try:
            await page.goto("http://localhost:8080", wait_until="networkidle")
            print("Loaded homepage")
        except Exception as e:
            print(f"Failed to load: {e}")
            return

        pdf_path = os.path.abspath("uploads/marks_4a20255a.pdf")
        excel_path = os.path.abspath("uploads/caste_4a20255a.xlsx")

        # Set files
        await page.locator('input[accept=".pdf"]').set_input_files(pdf_path)
        print("Set PDF file")
        await page.locator('input[accept=".xlsx,.xls"]').set_input_files(excel_path)
        print("Set Excel file")

        # Click Run Extraction
        await page.get_by_text("Run Extraction").click()
        print("Clicked Run Extraction")

        # Wait for API response or a specific element on page indicating success
        # Wait until 'Analysis Complete' toast appears or loading spinner goes away
        try:
            await page.get_by_text("Analysis Complete", exact=False).wait_for(state="visible", timeout=30000)
            print("Analysis complete toast appeared")
        except:
            print("Toast not found, waiting a bit...")
            await page.wait_for_timeout(5000)

        # Get UI data to validate it
        ui_data = {}
        ui_data["html"] = await page.content()

        with open("e2e_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "logs": logs,
                "ui_data": ui_data
            }, f, indent=2)

        print("Done")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
