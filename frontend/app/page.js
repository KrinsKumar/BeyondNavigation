"use client"

import Image from 'next/image'
import axios from "axios";
import { useState, useEffect } from "react";

export default function Home() {
  const [image, setImage] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [warning, setWarning] = useState(false);
  const [loading, setLoading] = useState(false);


  // multiple image input change
  const handleMultipleImage = (event) => {
    const files = [...event.target.files];
    setImage(files);
    setWarning(false)

    const previews = [];
    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = () => {
        previews.push(reader.result);
        if (previews.length === files.length) {
          setImagePreviews(previews);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  // multile image upload
  const miltipleImageUpload = async (e) => {
    e.preventDefault();

    if (image.length === 0) {
      setWarning(true)
      return
    }
 
    document.getElementById('my_modal_2').close()

    let formData = new FormData();

    Array.from(image).forEach((item) => {
      formData.append("images", item);
    });

    const url = "http://localhost:8000/api/multiple";

    setLoading(true);

    axios
      .post(url, formData)
      .then((result) => {
        console.log("Result", result);
      })
      .catch((err) => {
        console.log("Error: ", err);
      });

     // setLoading(false);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="upload">

        <button className="btn" onClick={()=>document.getElementById('my_modal_2').showModal()}>Upload Image</button>
        <dialog id="my_modal_2" className="modal">
          <div className="modal-box">
            <h3 className="font-bold text-lg">Hello!</h3>
            <p className="py-4">
              {
                warning ? `Whoopse, looks like you haven't uploaded any image yet!` :
                `Press ESC key or click outside to close`
              }
            </p>
            <div>
              {imagePreviews?.map((preview, index) => (
                <img
                  key={index}
                  src={preview}
                  alt={`Preview ${index}`}
                  style={{ width: "200px", height: "auto" }}
                />
              ))}
            </div>

            <br /><br />

            <form onSubmit={miltipleImageUpload}>
              <input type="file" onChange={handleMultipleImage} className="file-input file-input-bordered file-input-accent w-full max-w-xs" />
              <br /><br />
              <button className="btn btn-accent uploadBtn" type='submit'>Upload</button>
            </form> 
          </div>
          <form method="dialog" className="modal-backdrop">
            <button>close</button>
          </form>
        </dialog>

        <br /><br />
        {loading && <>Processing Image<span className="loading loading-ball loading-lg"></span></>}

      </div>
    </main>
  )
}

