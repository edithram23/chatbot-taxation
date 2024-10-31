# Selenium PDF Scraper

This project is a Python-based web scraping tool that uses Selenium to automate the process of downloading PDF, and RAR files from websites. It includes functions to navigate specific pages, collect links, download resources, and extract content from RAR files.

## Features

- Automated download of PDFs, text files, and RAR archives.
- Extracts RAR files using 7-Zip for further processing.
- Flexible options to target specific sections of webpages for file extraction.

## Requirements

- Selenium
- Microsoft Edge WebDriver
- Requests
- Rarfile (optional, for .rar handling)

Ensure you have 7-Zip installed at `C:\Program Files\7-Zip\7z.exe` for extracting `.rar` files.

## Usage

This script is designed to help automate the downloading of files from web pages. Below is an example of how to use it.

## Customization

- **Download Directory**: Change the `download_dir` in the `__init__` method of the `WebDriver` class.
- **WebDriver**: Ensure Edge WebDriver is correctly set up in your system.
- **RAR Extraction**: Update the path to `7-Zip` if necessary.
- The code be used to extract PDFs from a URL (or) iterate through a path and get the PDFs. Based on the user needs it can be changes.

