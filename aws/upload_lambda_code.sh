#!/bin/bash

# Function to zip and upload a Lambda function
zip_and_upload() {
    local function_name=$1
    local s3_bucket="fimarin-phucnguyen"
    local s3_key="lambda_functions/${function_name}.zip"

    echo "Zipping ${function_name}.py..."
    zip -j "aws/${function_name}.zip" "aws/${function_name}.py"

    echo "Uploading ${function_name}.zip to S3..."
    aws s3 cp "aws/${function_name}.zip" "s3://${s3_bucket}/${s3_key}"

    echo "Cleaning up..."
    rm "aws/${function_name}.zip"

    echo "${function_name} has been zipped and uploaded successfully."
}

# Zip and upload classify_articles
zip_and_upload "classify_articles"
zip_and_upload "crawl_thitruongtaichinhtiente"
zip_and_upload "crawl_thoibaonganhang"
zip_and_upload "generate_weekly_newsletter"
zip_and_upload "get_newsletter_list"
zip_and_upload "serve_newsletter"

echo "All operations completed successfully."
