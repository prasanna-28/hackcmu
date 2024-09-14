import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { FileText, Loader, Upload } from "lucide-react";

type ScreenType = "upload" | "loading" | "result";

interface VideoData {
  id: string;
  title: string;
  description: string;
  duration: string;
}

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [currentScreen, setCurrentScreen] = useState<ScreenType>("upload");
  const [videos, setVideos] = useState<VideoData[]>([]);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    setCurrentScreen("loading");

    const formData = new FormData();
    formData.append("file", acceptedFiles[0]);

    try {
      const response = await fetch("http://localhost:8888/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setFileId(data.file_id);
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setCurrentScreen("upload");
    }
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const checkStatus = async () => {
      if (fileId) {
        try {
          const response = await fetch(
            `http://localhost:8888/status?file_id=${fileId}`
          );
          const data = await response.json();

          if (data.status === "processing") {
            setStatus(data.status);
          } else if (data.status === "done") {
            setImageUrl(data.results.pdf); // Assuming data.results.pdf is actually a PNG URL
            setVideos(
              data.results.videos.map((video: any) => ({
                id: video.videoId,
                title: video.title,
                description: video.description,
                duration: video.duration,
              }))
            );
            setCurrentScreen("result");
            clearInterval(intervalId);
          }
        } catch (error) {
          console.error("Error:", error);
          clearInterval(intervalId);
        }
      }
    };

    if (currentScreen === "loading" && fileId) {
      intervalId = setInterval(checkStatus, 1000);
    }

    return () => clearInterval(intervalId);
  }, [currentScreen, fileId]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
    },
  });

  const renderUploadScreen = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex flex-col items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-3xl w-full">
        <h1 className="text-4xl md:text-6xl font-bold text-center mb-8 text-gray-800 leading-tight">
          I missed my lecture...😔
        </h1>
        <p className="text-xl text-center mb-4 text-gray-600">Now what?</p>
        <p className="text-xl text-center mb-8 text-gray-600">
          Upload or drag and drop any lecture notes to get tailored tutorials
          for your lecture.
        </p>

        <div
          {...getRootProps()}
          className={`w-full p-8 border-4 border-dashed rounded-lg text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? "border-blue-500 bg-blue-50 scale-105"
              : "border-gray-300 hover:border-blue-400 hover:bg-blue-50"
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-16 w-16 text-blue-500 mb-4" />
          <p className="text-xl font-semibold mb-2">
            {isDragActive
              ? "Drop the files here..."
              : "Upload or drag & drop files here"}
          </p>
          <p className="text-gray-500">Accepted file types: PDF, PNG, JPG</p>
        </div>

        {files.length > 0 && (
          <div className="mt-6 bg-gray-100 rounded-lg p-4">
            <h2 className="text-lg font-semibold mb-2">Uploaded files:</h2>
            <ul className="list-disc list-inside">
              {files.map((file) => (
                <li key={file.name} className="text-gray-600">
                  {file.name}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );

  const renderLoadingScreen = () => (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <Loader className="h-16 w-16 text-blue-500 animate-spin mb-4" />
      <p className="text-xl font-semibold">Processing your file...</p>
      <p className="text-lg text-gray-600 mt-2">Status: {status}</p>
    </div>
  );

  const renderResultScreen = () => (
    <div className="min-h-screen bg-gray-100 flex flex-col p-4">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="md:w-1/2">
          <h2 className="text-2xl font-semibold mb-2">Related Videos</h2>
          <div className="space-y-4">
            {videos.map((video) => (
              <div key={video.id} className="w-full max-w-2xl mb-8">
                <h3 className="text-lg font-semibold mt-2">{video.title}</h3>
                <p className="text-sm text-gray-600">{video.description}</p>
                <iframe
                  src={`https://www.youtube.com/embed/${video.id}`}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  title={video.title}
                  className="w-full aspect-video rounded-lg shadow-lg"
                />

                <p className="text-sm text-gray-500">
                  Duration: {video.duration.slice(2)}
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className="md:w-1/2">
          <h2 className="text-2xl font-semibold mb-2">Lecture Notes</h2>
          {imageUrl && (
            <div className="overflow-auto max-h-screen">
              <img src={imageUrl} alt="Generated content" className="w-full" />
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {currentScreen === "upload" && renderUploadScreen()}
      {currentScreen === "loading" && renderLoadingScreen()}
      {currentScreen === "result" && renderResultScreen()}
    </>
  );
}

export default App;
