from smolagents import tool
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = None

@tool
def search_item_ctrl_f(text: str, nth_result: int = 1) -> str:
    """
    Searches for text on the current page via Ctrl + F and jumps to the nth occurrence.
    Args:
        text: The text to search for
        nth_result: Which occurrence to jump to (default: 1)
    """
    if driver:
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
        if nth_result > len(elements):
            raise Exception(f"Match n°{nth_result} not found (only {len(elements)} matches found)")
        result = f"Found {len(elements)} matches for '{text}'."
        elem = elements[nth_result - 1]
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        result += f"Focused on element {nth_result} of {len(elements)}"
    return result

@tool
def go_back() -> None:
    """Goes back to previous page."""
    if driver:
        driver.back()

@tool
def close_popups() -> str:
    """
    Closes any visible modal or pop-up on the page. Use this to dismiss pop-up windows!
    This does not work on cookie consent banners.
    """
    if driver:
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
