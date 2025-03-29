import csv
import tkinter
import tkinter.filedialog
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from tkinter import *
from tkinter import ttk


file_data = []
auth = False
doc_id = ""
doc_url = ""
date = ""
driver = webdriver.Chrome()
not_processed = []

def get_file():
    global file_data
    global text_box
    file_data = []
    fh = tkinter.filedialog.askopenfile()
    reader = csv.reader(fh)
    for row in reader:
        file_data.append(row)
    for item in file_data:
        row_str = " | ".join(item) + "\n"
        text_box.insert(END, row_str)


def set_auth():
    global auth
    auth = True


def open_auth_page():
    global auth
    global driver
    global doc_id, doc_url, date, doc_id_var, url_var, date_var
    doc_id = doc_id_var.get()
    doc_url = url_var.get()
    date = date_var.get()
    print("ID: " + doc_id + "\n")
    print("URL: " + doc_url + "\n")
    print("Date: " + date + "\n")
    url = "https://gdbs.socar.ge/"
    driver.get(url)
    print("Auth page opened")
    set_auth()


def start_robot():
    global driver
    global auth
    global root
    global doc_id, doc_url, date
    mp_id = "MeterPointId_AdminNumber"
    mp_input_id = "AdminNumber"
    search_btn_id = "search"
    equ_input_id = "s2id_MeteringEquipmentId"
    options_class = "select2-result-label"
    equ_select_class = "select2-results"
    new_value_input_id = "CurrentValue"
    consumption_id = "Consumption"
    date_input_id = "ReadingDate"
    doc_id_input_id = "OperationAttribute_DocId"
    url_input_id = "OperationAttribute_WebUrl"
    is_mricxveli = False
    possible_options = ["კორექტორი", "მრიცხველი"]
    control_checkbox_id = "IsControl"
    div_success_class = "alert-success-msg"
    clean_btn_value = "გასუფთავება"
    cross_clear_btn_class = "clear"
    # submit_btn type=submit
    if auth:
        root.wm_state("iconic")
        driver.maximize_window()
        button = driver.find_element(By.XPATH, '//*[@title="ახლის დამატება"]')
        button.click()
        for row in range(len(file_data)):
            mp = file_data[row][1]
            print(mp + " | " + file_data[row][2] + " | " + file_data[row][3])
            for option_index in range(2):
                while True:
                    try:
                        mp_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.ID, mp_id))
                        )
                        mp_field.click()
                        mp_input = WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.ID, mp_input_id))
                        )
                        mp_input.send_keys(mp)

                        search_btn = driver.find_element(By.ID, search_btn_id)
                        search_btn.send_keys(Keys.RETURN)
                        down_arrow = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "fa-chevron-down"))
                        )
                        down_arrow.click()
                        break
                    except TimeoutException:
                        continue

                div_list = []
                while len(div_list) != 3:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, equ_input_id))).click()
                        div_list = driver.find_elements(By.CLASS_NAME, options_class)
                    except StaleElementReferenceException:
                        continue
                    except NoSuchElementException:
                        continue
                    except ElementClickInterceptedException:
                        continue
                div_list = div_list[1:]
                print("Options length:" + str(len(div_list)))
                options = [div.get_attribute("innerText") for div in div_list]
                current_option = possible_options[option_index]
                select_option_index = None
                for i in range(len(options)):
                    if re.match(r'[0-9]+ - ' + current_option, options[i]) is not None:
                        select_option_index = i+1
                if current_option == "მრიცხველი":
                    is_mricxveli = True
                else:
                    is_mricxveli = False

                equ_select_options = driver.find_elements(By.CLASS_NAME, "select2-result")

                print(current_option + " ინდექსი: " + str(select_option_index))
                equ_select_options[select_option_index].click()
                new_value_input = driver.find_element(By.ID, new_value_input_id)

                option_value = file_data[row][3 if is_mricxveli else 2]
                new_value_input.send_keys(option_value)
                consumption_delta = None

                date_input = driver.find_element(By.ID, date_input_id)
                date_input.send_keys(date)
                date_input.send_keys(Keys.ENTER)

                while True:
                    consumption_delta_input = driver.find_element(By.ID, consumption_id)
                    consumption_delta_str = consumption_delta_input.get_attribute("value")
                    if len(consumption_delta_str) != 0:
                        print("str: " + consumption_delta_str)
                        consumption_delta = int(consumption_delta_str)
                        print("numeric: " + str(consumption_delta))
                        break
                    else:
                        continue

                if consumption_delta < 0:
                    not_processed.append([mp, current_option])
                    driver.find_element(By.CSS_SELECTOR, "[value='გასუფთავება'").click()
                    driver.find_element(By.CLASS_NAME, cross_clear_btn_class).click()
                    continue

                doc_id_input = driver.find_element(By.ID, doc_id_input_id)
                doc_id_input.send_keys(doc_id)

                url_input = driver.find_element(By.ID, url_input_id)
                url_input.send_keys(doc_url)
                # driver.close()

                if is_mricxveli:
                    control_checkbox = driver.find_element(By.ID, control_checkbox_id)
                    control_checkbox.click()

                submit_btn = driver.find_element(By.CSS_SELECTOR, "[type='submit']")
                submit_btn.click()
            #     check if success msg present
                try:
                    div_success = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, div_success_class)))
                except TimeoutException:
                    print("Couldn't process row")
        driver.close()
        get_log_file()
    else:
        print("Not authorized")


def get_log_file():
    if len(not_processed) > 0:
        with open("not_processed.csv", "w", encoding="UTF-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for item in not_processed:
                writer.writerow(item)
            print("Writing finished")
    else:
        print("Fully processed the input file")


# main GUI root
root = Tk()
root.title("Socar Robota")
root.geometry("800x400")

doc_id_var = StringVar()
url_var = StringVar()
date_var = StringVar()

main_frame = ttk.Frame(root, padding="50")
main_frame.grid()

text_box = Text(root, width=80, height=15, wrap=NONE)
text_box.grid(row=5, column=0)
load_data_btn = ttk.Button(main_frame, text="Select file", command=get_file)
load_data_btn.grid(row=3, column=0)
auth_done_btn = ttk.Button(main_frame, text="Auth Check", command=open_auth_page)
auth_done_btn.grid(row=3, column=1)
start_btn = ttk.Button(main_frame, text="Start", command=start_robot)
start_btn.grid(row=3, column=2)
text_box.grid(row=4, column=0)
doc_id_label = ttk.Label(main_frame, text="Doc ID:") 
doc_id_label.grid(row=0, column=0)
doc_id_entry = ttk.Entry(main_frame, textvariable=doc_id_var)
doc_id_entry.grid(row=0, column=1)
url_label = ttk.Label(main_frame, text="URL:")
url_label.grid(row=1, column=0)
url_entry = ttk.Entry(main_frame, textvariable=url_var)
url_entry.grid(row=1, column=1)
date_label = ttk.Label(main_frame, text="Date:")
date_label.grid(row=2, column=0)
date_entry = ttk.Entry(main_frame, textvariable=date_var)
date_entry.grid(row=2, column=1)
root.mainloop()


# input file normalized
# date picker
# GUI
# robot
# failure control