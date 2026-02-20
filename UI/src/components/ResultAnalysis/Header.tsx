import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import React from "react";

interface HeaderProps {
  metadata: any;
  onChange?: (meta: {
    academic_year: string;
    department: string;
    exam_session: string;
    result_date: string;
  }) => void;
}

export const Header: React.FC<HeaderProps> = ({ metadata, onChange }) => {
  const [academicYear, setAcademicYear] = React.useState(
    metadata?.academic_year || ""
  );
  const [department, setDepartment] = React.useState(
    metadata?.department || ""
  );
  const [examSession, setExamSession] = React.useState(
    metadata?.exam_session || ""
  );
  const [resultDate, setResultDate] = React.useState(
    metadata?.result_date || ""
  );

  // Keep local state in sync when metadata from backend changes
  React.useEffect(() => {
    if (!metadata) return;
    setAcademicYear(metadata.academic_year || "");
    setDepartment(metadata.department || "");
    setExamSession(metadata.exam_session || "");
    setResultDate(metadata.result_date || "");
  }, [metadata]);

  // Notify parent whenever header fields change
  React.useEffect(() => {
    if (!onChange) return;
    onChange({
      academic_year: academicYear,
      department,
      exam_session: examSession,
      result_date: resultDate,
    });
  }, [academicYear, department, examSession, resultDate, onChange]);

  return (
    <div className="space-y-6 animate-fade-in">

      {/* ===== TOP HEADER ===== */}
      <div className="flex flex-col md:flex-row items-center gap-6 p-8 bg-gradient-to-br from-primary via-primary to-blue-700 rounded-3xl text-white shadow-xl">

        {/* Logo */}
        <div className="flex-shrink-0 relative">
          <div className="absolute inset-0 rounded-full bg-white opacity-20 blur-2xl"></div>

          <img
            src="/logo.png"
            alt="Soundarya Institute Logo"
            className="relative h-32 md:h-36 object-contain bg-white rounded-full p-3 shadow-2xl"
          />
        </div>

        {/* Institute Text */}
        <div className="text-center md:text-left space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
            Soundarya Educational Trust (Regd.)
          </h1>

          <h2 className="text-xl md:text-2xl font-semibold">
            SOUNDARYA INSTITUTE OF MANAGEMENT AND SCIENCE
          </h2>

          <p className="text-sm opacity-90">
            Soundarya Nagar, Bengaluru, Karnataka 560073
          </p>

          <div className="inline-block mt-2 px-4 py-1.5 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium">
            Accredited by NAAC
          </div>
        </div>
      </div>

      {/* ===== RESULT ANALYSIS DETAILS ===== */}
      <div className="bg-card p-8 rounded-3xl shadow-lg border border-border/50 space-y-6">
        <h3 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          RESULT ANALYSIS
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          {/* Academic Year */}
          <div className="space-y-2">
            <Label>Academic Year</Label>
            <Input
              placeholder="Eg: 2024-25"
              value={academicYear}
              onChange={(e) => setAcademicYear(e.target.value)}
              className="rounded-xl"
            />
          </div>

          {/* Department Dropdown */}
          <div className="space-y-2">
            <Label>Program / Department</Label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full rounded-xl border px-3 py-2 bg-background"
            >
              <option value="">Select Department</option>
              <option value="BCA">BCA</option>
              <option value="BBA">BBA</option>
              <option value="BCom">BCom</option>
            </select>
          </div>

          {/* Exam Session Dropdown */}
          <div className="space-y-2">
            <Label>BU Examination Month</Label>
            <select
              value={examSession}
              onChange={(e) => setExamSession(e.target.value)}
              className="w-full rounded-xl border px-3 py-2 bg-background"
            >
              <option value="">Select Exam Session</option>
              <option value="June">June</option>
              <option value="July">July</option>
              <option value="November">November</option>
              <option value="December">December</option>
            </select>
          </div>

          {/* Calendar Picker */}
          <div className="space-y-2">
            <Label>Date of Declaration</Label>
            <Input
              type="date"
              value={resultDate}
              onChange={(e) => setResultDate(e.target.value)}
              className="rounded-xl"
            />
          </div>

        </div>
      </div>
    </div>
  );
};
