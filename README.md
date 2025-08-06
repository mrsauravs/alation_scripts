# **`OpenAPI Upload Script: Usage Guide`**

`This guide provides comprehensive instructions to set up and run the update_openapi_and_upload.py script for validating and uploading OpenAPI YAML files to the ReadMe API platform. The script supports both Swagger CLI (OpenAPI 3.0) and Redocly CLI (OpenAPI 3.1) validation.`

## **`Set Up the Environment`**

`1. Install Python 3.8+`

```
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

`2. Install Node.js (v20.19.0 or higher recommended).`

`3. Verify installation:`

```
node -v
npm -v
```

`4. Install dependencies: Required Python packages`

```
pip install -r requirements.txt
```

**`Note:`** `If requirements.txt is missing, install manually:`

```
pip install python-dotenv pyyaml requests
```

``4. Clone the `alation` GitHub repository in your local system under the `Developer` folder.``

`Directory Expectations`

`The script expects the following Alation repo structure locally:`

```
~/Developer/alation/
├── django/
│   └── static/swagger/specs/
│       ├── data_products.yaml
│       ├── logical_metadata/
│       ├── common/
│       └── data_products/
```

`5. Login to ReadMe and copy the ReadMe key.`

`6. Create .env file in the script directory and paste the ReadMe key in the file:`

```
README_API_KEY=your_readme_api_key_here
```

## **`Run the Script`**

### **`Syntax`**

```
python update_openapi_and_upload.py <filename> <version> [--dry-run] [--local]
```

### **`Arguments`**

* `<filename>: Name of the YAML file (without .yaml extension).`  
* `<version>: ReadMe version string to update/create.`  
* `--dry-run: Skip upload, run validations only.`  
* `--local: Use a local YAML file instead of pulling from repo.`

### **`Steps`**

1. `Run the script with --dry-run first to validate the OpenAPI spec.` 

`Example:`

```
python update_openapi_and_upload.py data_products 2025.1.5 --dry-run
```

### 

2. `During --dry-run, the script prompts the validation the following options:`  
* `1. Swagger CLI (OpenAPI 3.0)`  
* `2. Redocly CLI (OpenAPI 3.1)`  
* `3. Both`

**`Note:`** `Choose based on your YAML version. For OpenAPI 3.1 files, use Redocly.`

3. ``Verify the log file `openapi_upload` to check validation errors.``  
   * `If errors exist, contact the API developer to resolve the issues.`  
4. `When all issues are resolved, rerun the script without --dry-run to upload the YAML file to ReadMe.`

