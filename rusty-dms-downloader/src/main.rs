use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Write};
use std::thread;
use std::time::{Duration};
use chrono::prelude::*;

fn download_image(url: &str, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Send a GET request to the URL
    let response = reqwest::blocking::get(url)?;

    // Check if the request was successful (status code 200)
    if !response.status().is_success() {
        return Err("Failed to download image".into());
    }

    // Read the response body as bytes
    let image_data = response.bytes()?;

    // Write the image data to a file
    let mut output_file = File::create(output_path)?;
    output_file.write_all(&image_data)?;

    println!("Image downloaded successfully!");
    Ok(())
}

fn main() -> io::Result<()> {
    let mut urls = HashMap::new();
    urls.insert("frame_3D1", "https://dallasmakerspace.org/cameras/frame_3D1.jpg");
    urls.insert("frame_3D2", "https://dallasmakerspace.org/cameras/frame_3D2.jpg");
    urls.insert("frame_Auto1", "https://dallasmakerspace.org/cameras/frame_Auto1.jpg");
    urls.insert("frame_CeramicsJewelry1", "https://dallasmakerspace.org/cameras/frame_CeramicsJewelry1.jpg");
    urls.insert("frame_CeramicsJewelry2", "https://dallasmakerspace.org/cameras/frame_CeramicsJewelry2.jpg");
    urls.insert("frame_Laser1", "https://dallasmakerspace.org/cameras/frame_Laser1.jpg");
    urls.insert("frame_MachineShop1", "https://dallasmakerspace.org/cameras/frame_MachineShop1.jpg");
    urls.insert("frame_MetalShop1", "https://dallasmakerspace.org/cameras/frame_MetalShop1.jpg");
    urls.insert("frame_MetalShop2", "https://dallasmakerspace.org/cameras/frame_MetalShop2.jpg");
    urls.insert("frame_MetalShop3", "https://dallasmakerspace.org/cameras/frame_MetalShop3.jpg");
    urls.insert("frame_WoodShop1", "https://dallasmakerspace.org/cameras/frame_WoodShop1.jpg");
    urls.insert("frame_WoodShop2", "https://dallasmakerspace.org/cameras/frame_WoodShop2.jpg");
    urls.insert("frame_WoodShop3", "https://dallasmakerspace.org/cameras/frame_WoodShop3.jpg");
    urls.insert("frame_WoodShop4", "https://dallasmakerspace.org/cameras/frame_WoodShop4.jpg");
    let output_dir = "./images/";               // Directory to save downloaded images

    loop {
        // Get current date and time
        let now = Local::now();
        let formatted_time = now.format("%Y-%m-%d-%H-%M-%S").to_string();

        // round to the nearest 5 minutes
        let rounded_time = now.minute() / 5 * 5;
        let formatted_time = now.with_minute(rounded_time).unwrap().format("%Y-%m-%d-%H-%M-%S").to_string();
        
        for (name, url) in &urls {
            print!("camera name: {} ======== ", name);

            // Create output path with formatted time
            let output_path = format!("{}{}_{}.jpg", output_dir, formatted_time, name);
    
            match download_image(url, &output_path) {
                Ok(()) => (),
                Err(err) => eprintln!("Error: {}", err),
            }
        }

        print!("Sleeping for 5 minutes, current time: {} \n", formatted_time);
        // Sleep for 5 minutes
        thread::sleep(Duration::from_secs(5 * 60));
    }
}
