import React from "react";
import { Header } from "@/components/ResultAnalysis/Header";
import { OverallSummary } from "@/components/ResultAnalysis/OverallSummary";
import { TopPerformers } from "@/components/ResultAnalysis/TopPerformers";
import { SubjectAnalysis } from "@/components/ResultAnalysis/SubjectAnalysis";
import { DemographicAnalysis } from "@/components/ResultAnalysis/DemographicAnalysis";
import { CentumAchievers } from "@/components/ResultAnalysis/Centum";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

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

  return <div>FIXED ✅</div>;
};

export default Index;