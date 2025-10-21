// pages/build-resume/components/steps/ContactStep.tsx
import { ResumeData } from '../../form/[template]/page';

interface ContactStepProps {
  data: ResumeData;
  onChange: (section: 'contact', data: unknown) => void;
}

export function ContactStep({ data, onChange }: ContactStepProps) {
  const handleChange = (field: string, value: string) => {
    onChange('contact', {
      ...data.contact,
      [field]: value,
    });
  };

  return (
    <div className="space-y-4">
      {/* Full Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Full Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={data.contact.fullName}
          onChange={(e) => handleChange('fullName', e.target.value)}
          placeholder="e.g., Daniel Johnson"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      {/* Job Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Job Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={data.contact.title}
          onChange={(e) => handleChange('title', e.target.value)}
          placeholder="e.g., Software Engineer"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <input
          type="text"
          value={data.contact.location}
          onChange={(e) => handleChange('location', e.target.value)}
          placeholder="e.g., San Francisco, CA 94122"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Phone & Email */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phone
          </label>
          <input
            type="tel"
            value={data.contact.phone}
            onChange={(e) => handleChange('phone', e.target.value)}
            placeholder="e.g., 508-278-2542"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            value={data.contact.email}
            onChange={(e) => handleChange('email', e.target.value)}
            placeholder="e.g., your.email@here.com"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
      </div>
    </div>
  );
}


