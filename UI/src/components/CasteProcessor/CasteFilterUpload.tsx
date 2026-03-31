import React, { useState, useRef, useEffect } from 'react';
import { useToast } from "@/hooks/use-toast";
import { UploadCloud, FileText, Loader2, CheckCircle, Trash2, ShieldCheck, Download, Users } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const ALLOWED_CASTES = ['General', 'OBC', 'SC', 'ST'];
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const CasteFilterUpload = () => {
  const { toast } = useToast();
  
  const [file, setFile] = useState<File | null>(null);
  const [caste, setCaste] = useState<string>('');
  
  const [isDragActive, setIsDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const [results, setResults] = useState<any | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const res = await fetch(`${API_URL}/files`);
      const data = await res.json();
      if (data.success) setUploadedFiles(data.files);
    } catch (err) {
      console.error("Failed to fetch files");
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files[0]?.type === 'application/pdf') {
      setFile(e.dataTransfer.files[0]);
    } else {
      toast({ title: "Error", description: "Only PDF files are allowed", variant: "destructive" });
    }
  };

  const handleUpload = () => {
    if (!file || !caste) {
        toast({ title: "Missing Input ⚠️", description: "Please select both file and caste category." });
        return;
    }

    setLoading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("caste", caste);

    const xhr = new XMLHttpRequest();
    
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        setProgress(Math.round((event.loaded * 100) / event.total));
      }
    };

    xhr.onload = () => {
      setLoading(false);
      setProgress(100);
      try {
        const data = JSON.parse(xhr.responseText);
        if (data.success) {
          toast({ title: "Analysis Complete 🎉", description: "Caste-filtered results loaded successfully." });
          setResults(data);
          fetchFiles();
        } else {
          toast({ title: "Upload Failed ❌", description: data.message, variant: "destructive" });
        }
      } catch (err) {
        toast({ title: "Error", description: "Server parsing error", variant: "destructive" });
      }
    };

    xhr.onerror = () => {
      setLoading(false);
      setProgress(0);
      toast({ title: "Network Error", description: "Failed to connect to server", variant: "destructive" });
    };

    xhr.open("POST", `${API_URL}/upload-caste-filter`);
    xhr.send(formData);
  };

  const deleteFile = async (filename: string) => {
    try {
      const res = await fetch(`${API_URL}/files/${filename}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        toast({ title: "File Removed", description: data.message });
        fetchFiles();
      }
    } catch {
      toast({ title: "Delete failed", variant: "destructive" });
    }
  };

  return (
    <div className="w-full space-y-8 animate-in fade-in duration-500">
      <Card className="border-emerald-100 dark:border-gray-800 shadow-xl overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-emerald-600 to-teal-700 text-white p-6">
          <div className="flex items-center gap-3">
             <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                <ShieldCheck className="w-6 h-6" />
             </div>
             <div>
                <CardTitle className="text-2xl font-bold tracking-tight">Caste-Based Result Engine</CardTitle>
                <p className="text-emerald-50 text-sm mt-1">Upload PDF to filter results by social category</p>
             </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-8 pb-10">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-10">
            
            {/* INPUT CONTROLS */}
            <div className="lg:col-span-2 space-y-8">
              <div className="space-y-3">
                <label className="text-sm font-semibold text-gray-600 dark:text-gray-400 flex items-center gap-2">
                   1. Select social category
                </label>
                <div className="grid grid-cols-2 gap-3">
                   {ALLOWED_CASTES.map((c) => (
                      <button
                        key={c}
                        onClick={() => setCaste(c)}
                        disabled={loading}
                        className={`py-3 px-4 rounded-xl border-2 transition-all font-medium text-sm
                          ${caste === c 
                            ? 'border-emerald-600 bg-emerald-50 text-emerald-700 ring-4 ring-emerald-100 dark:ring-emerald-900/20' 
                            : 'border-gray-100 bg-gray-50 text-gray-500 hover:border-emerald-200 dark:bg-gray-900 dark:border-gray-800'}`}
                      >
                        {c}
                      </button>
                   ))}
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                   2. Upload result document
                </label>
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={() => setIsDragActive(false)}
                  onDrop={handleDrop}
                  onClick={() => !loading && fileInputRef.current?.click()}
                  className={`relative group border-2 border-dashed flex flex-col items-center justify-center p-10 rounded-2xl cursor-pointer transition-all duration-300
                    ${isDragActive ? 'border-emerald-500 bg-emerald-50/50 scale-[0.98]' : 'border-gray-200 hover:border-emerald-400 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-900'}
                    ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className={`p-4 rounded-full transition-transform duration-300 group-hover:scale-110 ${isDragActive ? 'bg-emerald-100' : 'bg-gray-100 dark:bg-gray-800'}`}>
                    <UploadCloud className={`w-8 h-8 ${isDragActive ? 'text-emerald-600' : 'text-gray-400'}`} />
                  </div>
                  <p className="mt-4 text-sm font-medium text-gray-700 dark:text-gray-300">
                    {file ? <span className="text-emerald-600">{file.name}</span> : "Drop PDF or browse"}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">Standard Result Format (.pdf)</p>
                  <input 
                    type="file" 
                    accept=".pdf" 
                    hidden 
                    ref={fileInputRef} 
                    onChange={e => e.target.files && setFile(e.target.files[0])} 
                  />
                </div>
              </div>

              <Button
                onClick={handleUpload}
                disabled={!file || !caste || loading}
                className={`w-full py-7 rounded-2xl text-lg font-bold shadow-lg transition-transform hover:scale-[1.01] active:scale-[0.99]
                   ${loading ? 'bg-gray-400' : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700'}`}
              >
                {loading ? <><Loader2 className="w-6 h-6 animate-spin mr-2" /> Processing...</> : "Start Analysis"}
              </Button>

              {loading && (
                <div className="space-y-2">
                   <Progress value={progress} className="h-2 bg-gray-100" />
                   <p className="text-[10px] text-center font-bold uppercase tracking-wider text-emerald-600 animate-pulse">Running extraction algorithms...</p>
                </div>
              )}
            </div>

            {/* QUICK HISTORY */}
            <div className="lg:col-span-3 space-y-6">
               <div className="bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-6 border border-gray-100 dark:border-gray-800 h-full min-h-[400px]">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                       <Users className="w-5 h-5 text-emerald-600" /> Repository Log
                    </h3>
                    <span className="text-[10px] bg-white border px-2 py-1 rounded-full font-bold text-gray-400">{uploadedFiles.length} FILES</span>
                  </div>
                  
                  {uploadedFiles.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-gray-400 opacity-50">
                       <FileText className="w-12 h-12 mb-3" />
                       <p className="text-sm font-medium">No previous uploads found in workspace</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-3 max-h-[450px] overflow-y-auto pr-2 custom-scrollbar">
                      {uploadedFiles.slice().reverse().map(f => (
                        <div key={f} className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-xl group hover:shadow-md transition-all hover:border-emerald-200">
                          <div className="flex items-center gap-3 truncate">
                            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                               <FileText className="w-5 h-5" />
                            </div>
                            <div className="truncate">
                               <p className="text-sm font-bold text-gray-700 dark:text-gray-200 truncate">{f.split('_').slice(2).join('_') || f}</p>
                               <p className="text-[10px] text-gray-400 uppercase tracking-tighter">Uploaded {new Date(parseInt(f.split('_')[1]) * 1000).toLocaleDateString()}</p>
                            </div>
                          </div>
                          <button 
                            onClick={() => deleteFile(f)}
                            className="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                            title="Delete File"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
               </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* RESULTS DISPLAY SECTION */}
      {results?.success && (
        <div className="space-y-6 animate-in slide-in-from-bottom-8 duration-700">
          <div className="flex items-center justify-between">
             <div className="flex items-center gap-4">
                <div className="p-3 bg-emerald-100 text-emerald-700 rounded-2xl">
                   <CheckCircle className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-gray-800 dark:text-gray-100 tracking-tight">Social Category Analysis</h3>
                  <div className="flex gap-2 mt-1">
                    <span className="px-3 py-1 bg-emerald-600 text-white font-bold rounded-full text-[10px] uppercase shadow-lg shadow-emerald-200 dark:shadow-none">
                       {results.caste} Category
                    </span>
                    <span className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-500 font-bold rounded-full text-[10px] uppercase">
                       {results.data.total_filtered} Students matched
                    </span>
                  </div>
                </div>
             </div>
             <div className="flex gap-3">
                <Button variant="outline" className="rounded-xl font-bold border-gray-200 text-gray-600 hover:bg-gray-50 gap-2">
                   <Download className="w-4 h-4" /> Export Public
                </Button>
                <Button className="rounded-xl font-bold bg-emerald-600 hover:bg-emerald-700 shadow-lg shadow-emerald-200 dark:shadow-none gap-2">
                   <Download className="w-4 h-4" /> Download Result
                </Button>
             </div>
          </div>

          <Card className="rounded-3xl border-none shadow-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-[11px] text-gray-400 uppercase tracking-widest bg-gray-50/80 dark:bg-gray-900 border-b dark:border-gray-800">
                  <tr>
                    <th className="px-8 py-6 font-black">Registration</th>
                    <th className="px-8 py-6 font-black">Student Identity</th>
                    <th className="px-8 py-6 font-black text-center">Score Metric</th>
                    <th className="px-8 py-6 font-black text-center">Percentage</th>
                    <th className="px-8 py-6 font-black text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {results.data.students.length > 0 ? results.data.students.map((student: any) => (
                    <tr key={student.usn} className="hover:bg-emerald-50/30 dark:hover:bg-emerald-900/10 transition-colors">
                      <td className="px-8 py-5 font-mono font-bold text-gray-900 dark:text-gray-100 tracking-tighter">{student.usn}</td>
                      <td className="px-8 py-5">
                         <div className="font-bold text-gray-700 dark:text-gray-300">{student.name}</div>
                         <div className="text-[10px] text-gray-400 uppercase font-black">Undergraduate Scholar</div>
                      </td>
                      <td className="px-8 py-5 text-center">
                         <span className="font-black text-lg text-emerald-600">{student.overall_total}</span>
                         <span className="text-gray-300 mx-1">/</span>
                         <span className="text-[11px] font-bold text-gray-400">{student.overall_max}</span>
                      </td>
                      <td className="px-8 py-5 text-center">
                        <div className="inline-block px-4 py-2 bg-gray-100 dark:bg-gray-900 rounded-xl font-black text-emerald-600 border border-transparent hover:border-emerald-200 transition-all">
                           {student.percentage}%
                        </div>
                      </td>
                      <td className="px-8 py-5 text-center">
                         <span className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-sm ${
                           student.result === 'PASS' 
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                            : 'bg-rose-100 text-rose-700 border border-rose-200'}`}>
                           {student.result}
                         </span>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan={5} className="px-8 py-20 text-center">
                         <div className="inline-flex flex-col items-center">
                            <div className="p-4 bg-gray-50 rounded-full mb-4">
                               <Users className="w-12 h-12 text-gray-200" />
                            </div>
                            <p className="text-gray-500 font-bold">No students found matching <span className="text-emerald-600">"{results.caste}"</span> criteria in this document.</p>
                         </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
