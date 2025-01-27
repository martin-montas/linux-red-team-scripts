package main

import (
	"flag"
	"fmt"
	"net/http"
	"net/url"
	"sync"

	"github.com/PuerkitoBio/goquery"
)

// Allowed form tags
var allowedTags = []string{
	"form",
}

// Payloads to be used for form fields
var payloads = map[string]string{
	"username": "exampleuser",
	"password": "examplepass",
}

func scrapeAndSendRequest(pageURL string, wg *sync.WaitGroup) {
	// Fetch the page
	resp, err := http.Get(pageURL)
	if err != nil {
		fmt.Println("Error fetching page:", err)
		wg.Done()
		return
	}
	defer resp.Body.Close()

	// Parse the HTML
	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		fmt.Println("Error parsing page:", err)
		wg.Done()
		return
	}

	// Construct the full action URL
	actionURL, err := url.Parse(pageURL)
	if err != nil {
		fmt.Println("Error parsing page URL:", err)
		wg.Done()
		return
	}

	// Find all allowed form elements and process them
	for _, tag := range allowedTags {
		doc.Find(tag).Each(func(index int, item *goquery.Selection) {
			wg.Add(1)
			go threadedQuery(actionURL, item, wg)
		})
	}
	wg.Done()
}

func threadedQuery(actionURL *url.URL, form *goquery.Selection, wg *sync.WaitGroup) {
	defer wg.Done()

	action, exists := form.Attr("action")
	if !exists {
		fmt.Println("[!] Form action not found")
		return
	}

	actionURL, err := actionURL.Parse(action)
	if err != nil {
		fmt.Println("[!] Error parsing action URL:", err)
		return
	}

	// Create the payload based on form input fields
	formData := url.Values{}
	form.Find("input").Each(func(index int, item *goquery.Selection) {
		name, exists := item.Attr("name")
		if exists {
			if payload, ok := payloads[name]; ok {
				formData.Set(name, payload)
			}
		}
	})

	// Send the POST request
	resp, err := http.PostForm(actionURL.String(), formData)
	if err != nil {
		fmt.Println("[!] Error sending request:", err)
		return
	}
	defer resp.Body.Close()

	// Print the response status
	fmt.Println("[*] Response Status:", resp.Status)
}

func main() {
	var (
		url = flag.String("url", "http://127.0.0.1", "The URL for your target")
	)
	// Parse the flags
	flag.Parse()

	var wg sync.WaitGroup
	wg.Add(1)
	scrapeAndSendRequest(*url, &wg)
	wg.Wait()
}
