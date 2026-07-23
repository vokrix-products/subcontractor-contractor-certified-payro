import os, sys, time, json, tempfile, requests, traceback

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_SERVICE_KEY = os.environ['SUPABASE_SERVICE_KEY']
PRODUCT_ID = os.environ['PRODUCT_ID']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']

HEADERS = {
    'apikey': SUPABASE_SERVICE_KEY,
    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def process_file(source_path, result_path):
    # Dynamically import backend main processing function
    from main import process_payload  # product-specific module expected
    return process_payload(source_path, result_path)

def main():
    while True:
        try:
            # Poll pending jobs
            resp = requests.get(
                f'{SUPABASE_URL}/rest/v1/jobs',
                headers={**HEADERS, 'Prefer': 'return=representation'},
                params={
                    'status': 'eq.pending',
                    'job_type': 'eq.process_upload',
                    'product_id': f'eq.{PRODUCT_ID}'
                })
            if resp.status_code != 200:
                time.sleep(60)
                continue
            jobs = resp.json()
            if not jobs:
                time.sleep(60)
                continue

            for job in jobs:
                job_id = job['id']
                try:
                    # Download input file
                    file_path = job['input_file_path']
                    download_url = f'{SUPABASE_URL}/storage/v1/object/upload/{file_path}'
                    file_resp = requests.get(download_url, headers={
                        'apikey': SUPABASE_SERVICE_KEY,
                        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}'
                    })
                    if file_resp.status_code != 200:
                        raise Exception(f"Failed to download input file: {file_resp.text}")

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_in:
                        tmp_in.write(file_resp.content)
                        input_tmp = tmp_in.name

                    result_tmp = tempfile.mktemp(suffix='.json')
                    # Run product-specific processing
                    output = process_file(input_tmp, result_tmp)

                    # Write record to records table
                    record_payload = {
                        'product_id': PRODUCT_ID,
                        'customer_id': job.get('customer_id'),
                        'title': output['title'],
                        'status': output['status'],
                        'details': output.get('details', {}),
                        'source_file_path': file_path,
                        'due_date': output.get('due_date')
                    }
                    rec_resp = requests.post(
                        f'{SUPABASE_URL}/rest/v1/records',
                        headers={**HEADERS, 'Prefer': 'return=minimal'},
                        json=record_payload)
                    if rec_resp.status_code not in (200, 201):
                        raise Exception(f"Record insert failed: {rec_resp.text}")

                    # Upload result to results bucket
                    with open(result_tmp, 'rb') as f:
                        upload_res = requests.put(
                            f'{SUPABASE_URL}/storage/v1/object/results/{os.path.basename(result_tmp)}',
                            headers={
                                'apikey': SUPABASE_SERVICE_KEY,
                                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                                'Content-Type': 'application/octet-stream',
                                'x-upsert': 'true'
                            },
                            data=f)
                    if upload_res.status_code not in (200, 201):
                        raise Exception(f"Result upload failed: {upload_res.text}")

                    # Mark job completed
                    update_payload = {
                        'status': 'completed',
                        'output_file_path': f'results/{os.path.basename(result_tmp)}',
                        'result_summary': output.get('summary', ''),
                        'completed_at': 'now()'
                    }
                    update_res = requests.patch(
                        f'{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}',
                        headers={**HEADERS, 'Prefer': 'return=minimal'},
                        json=update_payload)
                    if update_res.status_code not in (200, 201):
                        raise Exception(f"Job update failed: {update_res.text}")

                except Exception as e:
                    traceback.print_exc()
                    # Mark job failed
                    fail_payload = {
                        'status': 'failed',
                        'result_summary': str(e),
                        'completed_at': 'now()'
                    }
                    requests.patch(
                        f'{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}',
                        headers={**HEADERS, 'Prefer': 'return=minimal'},
                        json=fail_payload)
                finally:
                    # cleanup temp files
                    if 'input_tmp' in locals() and os.path.exists(input_tmp):
                        os.unlink(input_tmp)
                    if 'result_tmp' in locals() and os.path.exists(result_tmp):
                        os.unlink(result_tmp)

        except Exception as e:
            traceback.print_exc()
        time.sleep(60)

if __name__ == '__main__':
    main()
