import { Header } from "@/components/ResultAnalysis/Header";
import { OverallSummary } from "@/components/ResultAnalysis/OverallSummary";
import { TopPerformers } from "@/components/ResultAnalysis/TopPerformers";
import { SubjectAnalysis } from "@/components/ResultAnalysis/SubjectAnalysis";
import { DemographicAnalysis } from "@/components/ResultAnalysis/DemographicAnalysis";
import { CentumAchievers } from "@/components/ResultAnalysis/Centum";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import React from "react";

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

  // UI metadata to send to backend (header + subject-wise)
  const [headerMeta, setHeaderMeta] = React.useState<{
    academic_year: string;
    department: string;
    exam_session: string;
    result_date: string;
  }>({
    academic_year: "",
    department: "",
    exam_session: "",
    result_date: "",
  });

  const [subjectMeta, setSubjectMeta] = React.useState<
    { subject: string; section: string; faculty: string }[]
  >([]);

  // ================= THEME INIT =================
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

  // ================= DOWNLOAD DOCX =================
  const downloadReport = async () => {
    try {
      const uiMeta = {
        academic_year: headerMeta.academic_year,
        department: headerMeta.department,
        exam_session: headerMeta.exam_session,
        // Use detected semester from backend metadata if available
        semester: metadata?.semester || "",
        result_date: headerMeta.result_date,
        subjects: subjectMeta,
      };

      const response = await fetch("https://result-engine-sims.onrender.com/generate-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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

      toast({
        title: "Download Started 📄",
        description: "Report downloaded successfully.",
      });

    } catch {
      toast({
        title: "Download Failed ❌",
        description: "Upload & Analyze first.",
      });
    }
  };

  const downloadPublicReport = async () => {
    try {
      const uiMeta = {
        academic_year: headerMeta.academic_year,
        department: headerMeta.department,
        exam_session: headerMeta.exam_session,
        // Use detected semester from backend metadata if available
        semester: metadata?.semester || "",
        result_date: headerMeta.result_date,
        subjects: subjectMeta,
      };

      const response = await fetch(
        "http://127.0.0.1:5000/generate-report?format=public",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ ui_meta: uiMeta }),
        }
      );

      if (!response.ok) throw new Error("Failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "Approved_Result_Analysis_Public.docx";
      document.body.appendChild(a);
      a.click();
      a.remove();

      toast({
        title: "Download Started 📄",
        description: "Report downloaded successfully.",
      });
    } catch {
      toast({
        title: "Download Failed ❌",
        description: "Upload & Analyze first.",
      });
    }
  };

  // ================= UPLOAD =================
  const handleUpload = async () => {
    if (!marksFile || !casteFile) {
      toast({
        title: "Missing Files ❌",
        description: "Please select both files.",
      });
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("marks", marksFile);
    formData.append("caste", casteFile);

    try {
      const response = await fetch("https://result-engine-sims.onrender.com/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error();

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
      setSummary (mapped);
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

      toast({
        title: "Analysis Complete 🎉",
        description: "All data loaded successfully.",
      });

    } catch {
      toast({
        title: "Upload Failed ❌",
        description: "Server error.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen transition-colors duration-300 bg-white dark:bg-gray-900 text-black dark:text-white pb-12 relative">
      {/* Watermark overlay (non-interactive) */}
      <div
        className="fixed inset-0 z-0 flex items-center justify-center"
        style={{ pointerEvents: "none", userSelect: "none" }}
        aria-hidden="true"
      >
        <img
          src="/watermark.PNG"
          alt="watermark"
          draggable={false}
          className="fixed bottom-6 right-6 w-24 opacity-50 pointer-events-none select-none z-10"
        />
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

        <div className="flex gap-4 justify-end flex-wrap">

          <Button onClick={toggleTheme} variant="outline">
            {theme === "dark" ? "☀ Light Mode" : "🌙 Dark Mode"}
          </Button>

          <label className="bg-primary text-white px-4 py-2 rounded cursor-pointer">
            Marks PDF
            <input type="file"
            hidden
            accept=".pdf"
            onChange={(e) => {const file = e.target.files?.[0] || null; setMarksFile(file);
          if (file) {
            toast({
            title: "Marks PDF Uploaded ✅",
            description: `${file.name} selected successfully.`,
          });
        }
      }}
    />
          </label>

          <label className="bg-secondary px-4 py-2 rounded cursor-pointer">
            Caste Excel
            <input
  type="file"
  hidden
  accept=".xlsx,.xls"
  onChange={(e) => {
    const file = e.target.files?.[0] || null;
    setCasteFile(file);

    if (file) {
      toast({
        title: "Caste Excel Uploaded ✅",
        description: `${file.name} selected successfully.`,
      });
    }
  }}
/>
          </label>

          <Button onClick={handleUpload} disabled={loading}>
            Upload & Analyze
          </Button>

          <Button onClick={downloadReport} className="flex items-center gap-2">
            <Download size={18} />
            Download Internal Result
          </Button>

          <Button onClick={downloadPublicReport} className="flex items-center gap-2" variant="secondary">
            <Download size={18} />
            Download Public Result
          </Button>

        </div>

        <Header metadata={metadata} onChange={setHeaderMeta} />
        <OverallSummary summary={summary} />
        <TopPerformers topPerformers={topPerformers} />
        <SubjectAnalysis subjects={subjects} onMetaChange={setSubjectMeta} />
        <DemographicAnalysis demographics={demographics} />
        <CentumAchievers centum={centum} />

      </div>

      {loading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-10 flex flex-col items-center gap-5">
            <div className="h-14 w-14 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xl font-semibold">
              Analyzing Results...
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
