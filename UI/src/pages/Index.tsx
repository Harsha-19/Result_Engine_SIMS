import React from "react";
import { Header } from "@/components/ResultAnalysis/Header";
import { OverallSummary } from "@/components/ResultAnalysis/OverallSummary";
import { TopPerformers } from "@/components/ResultAnalysis/TopPerformers";
import { SubjectAnalysis } from "@/components/ResultAnalysis/SubjectAnalysis";
import { DemographicAnalysis } from "@/components/ResultAnalysis/DemographicAnalysis";
import { CentumAchievers } from "@/components/ResultAnalysis/Centum";
import { Button } from "@/components/ui/button";
import { Download, LayoutDashboard, UserCheck, ShieldCheck } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CasteFilterUpload } from "@/components/CasteProcessor/CasteFilterUpload";

const API_URL = import.meta.env.VITE_API_URL || "https://result-engine-sims.onrender.com";

const Index = () => {
  const { toast } = useToast();

  const [metadata, setMetadata] = React.useState<any>(null);
  const [marksFile, setMarksFile] = React.useState<File | null>(null);
  const [casteFile, setCasteFile] = React.useState<File | null>(null);

  const [summary, setSummary] = React.useState<any[]>([]);
  const [topPerformers, setTopPerformers] = React.useState<any[]>([]);
  const [subjects, setSubjects] = React.useState<any[]>([]);
  const [demographics, setDemographics] = React.useState<any>(null);
  const [centum, setCentum] = React.useState<any[]>([]);

  const [loading, setLoading] = React.useState(false);
  const [theme, setTheme] = React.useState<"light" | "dark">("light");

  const [headerMeta, setHeaderMeta] = React.useState({
    academic_year: "",
    department: "",
    exam_session: "",
    result_date: "",
  });

  const [subjectMeta, setSubjectMeta] = React.useState<
    { subject: string; section: string; faculty: string }[]
  >([]);

  React.useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;

    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle("dark", savedTheme === "dark");
    } else {
      const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      const initialTheme = systemPrefersDark ? "dark" : "light";
      setTheme(initialTheme);
      document.documentElement.classList.toggle("dark", initialTheme === "dark");
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  const downloadReport = async () => {
    try {
      const uiMeta = {
        academic_year: headerMeta.academic_year,
        department: headerMeta.department,
        exam_session: headerMeta.exam_session,
        semester: metadata?.semester || "",
        result_date: headerMeta.result_date,
        subjects: subjectMeta,
      };

      const response = await fetch(`${API_URL}/generate-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ui_meta: uiMeta }),
      });

      if (!response.ok) throw new Error("Failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "Approved_Result_Analysis.docx";
      document.body.appendChild(a);
      a.click();
      a.remove();

      toast({ title: "Download Started 📄", description: "Report downloaded successfully." });

    } catch {
      toast({ title: "Download Failed ❌", description: "Upload & Analyze first." });
    }
  };

  const downloadPublicReport = async () => {
    try {
      const uiMeta = {
        academic_year: headerMeta.academic_year,
        department: headerMeta.department,
        exam_session: headerMeta.exam_session,
        semester: metadata?.semester || "",
        result_date: headerMeta.result_date,
        subjects: subjectMeta,
      };

      const response = await fetch(`${API_URL}/generate-report?format=public`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ui_meta: uiMeta }),
      });

      if (!response.ok) throw new Error("Failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "Approved_Result_Analysis_Public.docx";
      document.body.appendChild(a);
      a.click();
      a.remove();

      toast({ title: "Download Started 📄", description: "Report downloaded successfully." });

    } catch {
      toast({ title: "Download Failed ❌", description: "Upload & Analyze first." });
    }
  };
  const handleMarksFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setMarksFile(file);
      toast({ title: "Selection Successful ✅", description: `${file.name} uploaded successfully.` });
    } else {
      setMarksFile(null);
    }
  };

  const handleCasteFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCasteFile(file);
      toast({ title: "Selection Successful ✅", description: `${file.name} uploaded successfully.` });
    } else {
      setCasteFile(null);
    }
  };

  const handleUpload = async () => {
    if (!marksFile || !casteFile) {
      toast({ title: "Missing Files ❌", description: "Please select both files." });
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("marks", marksFile);
    formData.append("caste", casteFile);

    const uiMeta = {
      academic_year: headerMeta.academic_year,
      department: headerMeta.department,
      exam_session: headerMeta.exam_session,
      result_date: headerMeta.result_date,
      subjects: subjectMeta,
    };
    formData.append("ui_meta", JSON.stringify(uiMeta));

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Server error");
      }

      if (data.metadata) {
        setMetadata(data.metadata);
        setHeaderMeta({
          academic_year: data.metadata.academic_year || "",
          department: data.metadata.department || "",
          exam_session: data.metadata.exam_session || "",
          result_date: data.metadata.result_date || "",
        });
      }

      if (data.summary && typeof data.summary === "object") {
        const mapped = ["Boys", "Girls", "Total"].map((key) => ({
          category: key,
          studentsAppeared: data.summary[key]?.appeared ?? 0,
          distinction: data.summary[key]?.distinction ?? 0,
          firstClass: data.summary[key]?.first ?? 0,
          secondClass: data.summary[key]?.second ?? 0,
          passClass: data.summary[key]?.pass_class ?? 0,
          totalPassed: data.summary[key]?.passed ?? 0,
          totalFailed: data.summary[key]?.failed ?? 0,
          passPercentage: data.summary[key]?.pass_percentage ?? 0,
        }));
        setSummary(mapped);
      } else {
        setSummary([]);
      }

      if (data.rankers) setTopPerformers(data.rankers);
      if (data.subjects) {
        setSubjects(data.subjects);
        setSubjectMeta(
          data.subjects.map((s: any) => ({
            subject: s.subject,
            section: s.section || "",
            faculty: s.faculty || "",
          }))
        );
      }
      if (data.demographics) setDemographics(data.demographics);
      if (data.centum) setCentum(data.centum);

      toast({ title: "Analysis Complete 🎉", description: "All data loaded successfully." });

    } catch (err: any) {
      toast({
        title: "Upload Failed ❌",
        description:
          err.message === "File already uploaded"
            ? "👉 File already uploaded"
            : "Server error. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen transition-colors duration-300 bg-white dark:bg-gray-900 text-black dark:text-white pb-12 relative font-sans">
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

        <Tabs defaultValue="dashboard" className="w-full">
          <div className="flex items-center justify-between flex-wrap gap-6 mb-10 pb-6 border-b border-gray-100 dark:border-gray-800">
             <div className="space-y-1">
                <h1 className="text-3xl font-black tracking-tighter text-gray-900 dark:text-white">Academic Result Intelligence</h1>
                <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest">Enterprise Processing Suite v2.0</p>
             </div>

             <div className="flex items-center gap-4 bg-gray-50 dark:bg-gray-900 p-1.5 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-inner">
                <TabsList className="bg-transparent h-auto p-0 gap-1 border-none shadow-none">
                  <TabsTrigger 
                    value="dashboard" 
                    className="rounded-xl px-6 py-3 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-800 data-[state=active]:shadow-lg data-[state=active]:text-emerald-700 dark:data-[state=active]:text-emerald-400 font-bold text-xs uppercase tracking-widest transition-all gap-2"
                  >
                    <LayoutDashboard className="w-4 h-4" /> Comprehensive Analysis
                  </TabsTrigger>
                  <TabsTrigger 
                    value="caste" 
                    className="rounded-xl px-6 py-3 data-[state=active]:bg-white dark:data-[state=active]:bg-gray-800 data-[state=active]:shadow-lg data-[state=active]:text-emerald-700 dark:data-[state=active]:text-emerald-400 font-bold text-xs uppercase tracking-widest transition-all gap-2"
                  >
                    <ShieldCheck className="w-4 h-4" /> Category Processing
                  </TabsTrigger>
                </TabsList>
                
                <div className="w-[1px] h-6 bg-gray-200 dark:bg-gray-700 mx-1" />
                
                <Button onClick={toggleTheme} variant="ghost" size="icon" className="rounded-xl hover:bg-white dark:hover:bg-gray-800 transition-all">
                  {theme === "dark" ? "☀" : "🌙"}
                </Button>
             </div>
          </div>

          <TabsContent value="dashboard" className="space-y-12 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex gap-4 justify-end flex-wrap bg-gray-50/50 dark:bg-gray-900/50 p-4 rounded-3xl border border-gray-100 dark:border-gray-800 backdrop-blur-sm">
              <label className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-widest cursor-pointer transition-all shadow-lg shadow-indigo-100 dark:shadow-none min-w-[140px] text-center">
                1. Marks PDF
                <input
                  hidden
                  type="file"
                  accept=".pdf"
                  onChange={handleMarksFileChange}
                />
              </label>

              <label className="bg-amber-500 hover:bg-amber-600 text-white px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-widest cursor-pointer transition-all shadow-lg shadow-amber-100 dark:shadow-none min-w-[140px] text-center">
                2. Caste Excel
                <input
                  hidden
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleCasteFileChange}
                />
              </label>

              <Button 
                onClick={handleUpload} 
                disabled={loading}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl font-bold text-xs uppercase tracking-widest transition-all shadow-lg shadow-emerald-100 dark:shadow-none min-w-[160px]"
              >
                {loading ? "Processing..." : "Run Extraction"}
              </Button>

              <div className="w-px h-8 bg-gray-200 dark:bg-gray-800 mx-2 hidden sm:block" />

              <Button onClick={downloadReport} variant="outline" className="rounded-xl font-bold text-xs uppercase tracking-widest border-gray-200 hover:bg-gray-50 dark:border-gray-800">
                <Download className="w-4 h-4 mr-2" /> Internal Doc
              </Button>

              <Button onClick={downloadPublicReport} variant="outline" className="rounded-xl font-bold text-xs uppercase tracking-widest border-gray-200 hover:bg-gray-50 dark:border-gray-800">
                <Download className="w-4 h-4 mr-2" /> Public Doc
              </Button>
            </div>

            <Header metadata={metadata} onChange={setHeaderMeta} />
            <div className="grid grid-cols-1 gap-10">
              <OverallSummary summary={summary} />
              <TopPerformers topPerformers={topPerformers} />
              <SubjectAnalysis subjects={subjects} onMetaChange={setSubjectMeta} />
              <DemographicAnalysis demographics={demographics} />
              <CentumAchievers centum={centum} />
            </div>
          </TabsContent>

          <TabsContent value="caste" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
             <CasteFilterUpload />
          </TabsContent>
        </Tabs>

      </div>
    </div>
  );
};

export default Index;
