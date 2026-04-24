import { useSelector, useDispatch } from "react-redux";
import { updateField } from "../redux/formSlice";

const FormPanel = () => {
  const form = useSelector((state) => state.form);
  const dispatch = useDispatch();

  const handleChange = (field, value) => {
    dispatch(updateField({ field, value }));
  };

  const inputClasses =
    "w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all duration-200";
  const labelClasses = "block text-sm font-semibold text-gray-300 mb-2";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-4 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-white">📋 Log Interaction</h2>
        <p className="text-emerald-100 text-sm mt-1">Fill details for HCP interaction tracking</p>
      </div>

      {/* Form Fields */}
      <div className="space-y-4">
        {/* HCP Name */}
        <div>
          <label className={labelClasses}>👤 HCP Name</label>
          <input
            className={inputClasses}
            placeholder="e.g., Dr. Sharma, Dr. Patel"
            value={form.hcp_name}
            onChange={(e) => handleChange("hcp_name", e.target.value)}
          />
        </div>

        {/* Interaction Type */}
        <div>
          <label className={labelClasses}>🤝 Interaction Type</label>
          <select
            className={inputClasses}
            value={form.interaction_type}
            onChange={(e) => handleChange("interaction_type", e.target.value)}
          >
            <option value="">Select type...</option>
            <option value="visit">📍 Visit</option>
            <option value="call">☎️ Call</option>
            <option value="email">📧 Email</option>
            <option value="meeting">🏢 Meeting</option>
          </select>
        </div>

        {/* Interaction Date */}
        <div>
          <label className={labelClasses}>📅 Interaction Date</label>
          <input
            type="date"
            className={inputClasses}
            value={form.interaction_date}
            onChange={(e) => handleChange("interaction_date", e.target.value)}
          />
        </div>

        {/* Products Discussed */}
        <div>
          <label className={labelClasses}>💊 Products Discussed</label>
          <input
            className={inputClasses}
            placeholder="e.g., Aspirin, Paracetamol, Ibuprofen"
            value={form.products_discussed.join(", ")}
            onChange={(e) =>
              handleChange(
                "products_discussed",
                e.target.value.split(",").map((p) => p.trim())
              )
            }
          />
          <p className="text-xs text-gray-400 mt-1">Separate with commas</p>
        </div>

        {/* Discussion Summary */}
        <div>
          <label className={labelClasses}>📝 Discussion Summary</label>
          <textarea
            className={`${inputClasses} resize-none`}
            placeholder="Brief summary of the interaction..."
            value={form.discussion_summary}
            onChange={(e) => handleChange("discussion_summary", e.target.value)}
            rows="3"
          />
        </div>

        {/* Doctor Feedback */}
        <div>
          <label className={labelClasses}>💬 Doctor Feedback</label>
          <textarea
            className={`${inputClasses} resize-none`}
            placeholder="Doctor's feedback and comments..."
            value={form.doctor_feedback}
            onChange={(e) => handleChange("doctor_feedback", e.target.value)}
            rows="3"
          />
        </div>

        {/* Follow Up Action */}
        <div>
          <label className={labelClasses}>✅ Follow Up Action</label>
          <input
            className={inputClasses}
            placeholder="Next step or follow-up action..."
            value={form.follow_up_action}
            onChange={(e) => handleChange("follow_up_action", e.target.value)}
          />
        </div>

        {/* Sentiment - Enhanced with visual indicator */}
        <div>
          <label className={labelClasses}>😊 Sentiment</label>
          <div className="flex items-center gap-2">
            <select
              className={inputClasses}
              value={form.sentiment}
              onChange={(e) => handleChange("sentiment", e.target.value)}
            >
              <option value="">Select sentiment...</option>
              <option value="positive">😊 Positive</option>
              <option value="neutral">😐 Neutral</option>
              <option value="negative">😟 Negative</option>
            </select>
            
            {/* Visual Sentiment Badge */}
            {form.sentiment && (
              <div className={`px-3 py-2 rounded-full font-semibold text-sm whitespace-nowrap flex-shrink-0 ${
                form.sentiment === "positive" ? "bg-green-600 text-white" :
                form.sentiment === "neutral" ? "bg-yellow-600 text-white" :
                form.sentiment === "negative" ? "bg-red-600 text-white" : ""
              }`}>
                {form.sentiment === "positive" && "😊 Positive"}
                {form.sentiment === "neutral" && "😐 Neutral"}
                {form.sentiment === "negative" && "😟 Negative"}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Save Button */}
      <button className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold px-6 py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105">
        💾 Save Interaction
      </button>

      {/* Info Cards */}
      <div className="grid grid-cols-2 gap-3 pt-4">
        <div className="bg-slate-700 border border-slate-600 p-3 rounded-lg">
          <p className="text-xs text-gray-400">Total Fields</p>
          <p className="text-lg font-bold text-cyan-400">8</p>
        </div>
        <div className="bg-slate-700 border border-slate-600 p-3 rounded-lg">
          <p className="text-xs text-gray-400">Completed</p>
          <p className="text-lg font-bold text-emerald-400">
            {Object.values(form).filter((v) => v).length}/8
          </p>
        </div>
      </div>
    </div>
  );
};

export default FormPanel;