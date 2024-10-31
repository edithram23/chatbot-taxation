from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import rarfile
import requests
import os
import subprocess
from tqdm import tqdm

class WebDriver():
    def __init__(self,download_dir='../data/'):
        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True  
        edge_options.add_experimental_option('prefs', {
            "download.default_directory": download_dir,  # Change default directory for downloads
            "download.prompt_for_download": False,  # To auto download the PDF
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # It will not open PDF in Edge
        })
        self.options = edge_options
        self.driver = webdriver.Edge(options=self.options)

    
    def get_link(self,link,href,div_id=None):
        self.driver.get(link)
        self.driver.implicitly_wait(10)
        if(div_id!=None):
            parent_div = self.driver.find_element(By.ID, div_id)
            pdf_links = parent_div.find_elements(By.XPATH, href)
        else:
            pdf_links = self.driver.find_elements(By.XPATH, href)
        links = []
        for link in pdf_links:
            href = link.get_attribute('href')
            links+=[href]
        return  links
    
    def get_pdf(self,list_links,folder=None):
        for url in list_links:
            if(folder is None):
                folder = os.path.basename(url)
                os.makedirs(folder, exist_ok=True)
            down_url=[]
            down_url += self.get_link(url,href=".//a[contains(@href, '.pdf') or contains(@href, '.txt') or contains(@href, '.rar')]")
            if len(down_url) == 0:
                print(url)
                continue
            self.download(down_url,folder)
    
    def download(self, urls, folder):
        for file in urls:
            try:
                
                # print("==="*100+f"Downloading {file}"+"==="*100)
                file_name = os.path.basename(file)
                file_path = os.path.join(folder, file_name)
                data = requests.get(file, stream=True)

                with open(file_path, 'wb') as f:
                    f.write(data.content)

                if file_name.endswith('.rar'):
                    self.extract_rar_with_7zip(file_path, folder)
                    os.remove(file_path)
            except:
                print(file)
                    
    def extract_rar_with_7zip(self, rar_file, output_folder):
            """Extracts RAR files using 7-Zip."""
            try:
                subprocess.run(
                    ["C:\Program Files\\7-Zip\\7z.exe", "x", rar_file, f"-o{output_folder}", "-y"],
                    check=True,
                    stdout=subprocess.DEVNULL,  # Suppress standard output
                    stderr=subprocess.DEVNULL 
                )
            except subprocess.CalledProcessError as e:
                print(f"Error extracting {rar_file}: {e}")

                    
                
                
            

extract = WebDriver()
# posts = extract.get_link('https://www.icai.org/resources.shtml?mod=9',".//a[contains(@href, 'https://www.icai.org/post/')]","9")
# extract.get_pdf(posts)
final_CA = {
                'Paper-1-Advanced Accounting':['https://boslive.icai.org/sm_chapter_details.php?p_id=3&m_id=7',
                                               'https://boslive.icai.org/sm_chapter_details.php?p_id=3&m_id=8',
                                               'https://boslive.icai.org/sm_chapter_details.php?p_id=3&m_id=10'],
                
                'Paper-2-Corporate and Other Laws':['https://boslive.icai.org/sm_chapter_details.php?p_id=84&m_id=104',
                                                    'https://boslive.icai.org/sm_chapter_details.php?p_id=84&m_id=105',
                                                    'https://boslive.icai.org/sm_chapter_details.php?p_id=84&m_id=106'],
                
                'Paper-3-Taxation-INCOME-TAX-LAW':['https://boslive.icai.org/sm_chapter_details.php?p_id=87&m_id=110',
                                                   'https://boslive.icai.org/sm_chapter_details.php?p_id=87&m_id=120'],
                
                'Paper-3-Taxation-Goods-and-service-Tax':['https://boslive.icai.org/sm_chapter_details.php?p_id=94&m_id=119'],
                
                'Paper-4-Cost-and-management':['https://boslive.icai.org/sm_chapter_details.php?p_id=88&m_id=112',
                                               'https://boslive.icai.org/sm_chapter_details.php?p_id=88&m_id=111'],
                
                'Paper-5-Auditing and Ethics':['https://boslive.icai.org/sm_chapter_details.php?p_id=10&m_id=21',
                                               'https://boslive.icai.org/sm_chapter_details.php?p_id=10&m_id=22'],
                
                'Paper-6-Financial-Management':['https://boslive.icai.org/sm_chapter_details.php?p_id=85&m_id=107',
                                                'https://boslive.icai.org/sm_chapter_details.php?p_id=85&m_id=108'],
                
                'Paper-6-Strategic-Management':['https://boslive.icai.org/sm_chapter_details.php?p_id=86&m_id=109']
                
           }

inter_CA = {
    'Income-Tax Act' : ['https://incometaxindia.gov.in/Pages/acts/income-tax-act.aspx'],
    'Integrated Business Solutions (Multidisciplinary Case study with Strategic Management)' : ['https://boslive.icai.org/sm_chapter_details.php?p_id=18&m_id=74'],

    'Paper-1-Financial Reporting':['https://boslive.icai.org/sm_chapter_details.php?p_id=13&m_id=26',
                                   'https://boslive.icai.org/sm_chapter_details.php?p_id=13&m_id=27',
                                   'https://boslive.icai.org/sm_chapter_details.php?p_id=13&m_id=28',
                                   'https://boslive.icai.org/sm_chapter_details.php?p_id=13&m_id=29'],
    'Paper-2-Advanced Financial Management':['https://boslive.icai.org/sm_chapter_details.php?p_id=14&m_id=30'],
    'Paper-3-Advanced Auditing,Assurance and Professional Ethics':['https://boslive.icai.org/sm_chapter_details.php?p_id=15&m_id=31',
                                                                    'https://boslive.icai.org/sm_chapter_details.php?p_id=15&m_id=32',
                                                                    'https://boslive.icai.org/sm_chapter_details.php?p_id=15&m_id=33'],
    'Paper-4-Direct Tax Laws and International Taxation': ['https://boslive.icai.org/sm_chapter_details.php?p_id=16&m_id=43',
                                                            'https://boslive.icai.org/sm_chapter_details.php?p_id=16&m_id=44',
                                                            'https://boslive.icai.org/sm_chapter_details.php?p_id=16&m_id=34',
                                                            'https://boslive.icai.org/sm_chapter_details.php?p_id=16&m_id=42'],
    'Paper-5-Indirect Tax Laws':['https://boslive.icai.org/sm_chapter_details.php?p_id=17&m_id=35',
                                  'https://boslive.icai.org/sm_chapter_details.php?p_id=17&m_id=45',
                                  'https://boslive.icai.org/sm_chapter_details.php?p_id=17&m_id=46',
                                  'https://boslive.icai.org/sm_chapter_details.php?p_id=17&m_id=41']
}



for path,url in tqdm(final_CA.items()):
    print(path)
    os.makedirs(path, exist_ok=True)
    extract.get_pdf(url,folder=path)

extract.driver.close()