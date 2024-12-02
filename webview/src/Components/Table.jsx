import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import Swal from 'sweetalert2';

const Table = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editData, setEditData] = useState({
    company_name: '',
    meeting_name: '',
    meeting_datetime: '',
    wav_url: '',
    summary_txt_url: '',
    whole_meeting_txt_url: ''
  });
  const [editingId, setEditingId] = useState(null);

  const fetchMeetings = async () => {
    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/meetings/get-all-records/`);
      setMeetings(response.data.data);
      setLoading(false);
    } catch (err) {
      console.log(err);
      setError('데이터를 불러오는데 실패했습니다.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  const handleDelete = async (id) => {
    try {
      const result = await Swal.fire({
        title: '정말 삭제하시겠습니까?',
        text: "삭제된 데이터는 복구할 수 없습니다!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '삭제',
        cancelButtonText: '취소'
      });

      if (result.isConfirmed) {
        const response = await axios.delete(`${import.meta.env.VITE_API_URL}/meetings/delete-record/${id}`);
        
        if (response.data.status_code === 200) {
          await Swal.fire(
            '삭제 완료!',
            '회의 정보가 성공적으로 삭제되었습니다.',
            'success'
          );
          fetchMeetings();
        } else {
          throw new Error(response.data.message);
        }
      }
    } catch (err) {
      Swal.fire(
        '오류 발생!',
        err.message || '회의 정보 삭제 중 오류가 발생했습니다.',
        'error'
      );
    }
  };

  const handleDeleteAll = async () => {
    try {
      const result = await Swal.fire({
        title: '모든 데이터를 삭제하시겠습니까?',
        text: "삭제된 데이터는 복구할 수 없습니다!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '삭제',
        cancelButtonText: '취소'
      });

      if (result.isConfirmed) {
        const response = await axios.delete(`${import.meta.env.VITE_API_URL}/meetings/delete-all-records/`);
        
        if (response.data.message) {
          await Swal.fire(
            '삭제 완료!',
            '모든 회의 정보가 성공적으로 삭제되었습니다.',
            'success'
          );
          fetchMeetings();
        } else {
          throw new Error(response.data.message);
        }
      }
    } catch (err) {
      Swal.fire(
        '오류 발생!',
        err.message || '회의 정보 삭제 중 오류가 발생했습니다.',
        'error'
      );
    }
  };

  const paginatedMeetings = useMemo(() => {
    if (!meetings) return [];
    const startIndex = (currentPage - 1) * itemsPerPage;
    return meetings.slice(startIndex, startIndex + itemsPerPage);
  }, [meetings, currentPage, itemsPerPage]);

  const pageCount = useMemo(() => {
    if (!meetings) return 0;
    return Math.ceil(meetings.length / itemsPerPage);
  }, [meetings?.length, itemsPerPage]);

  const handleEditClick = async (id) => {
    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/meetings/get-record/${id}`);
      const { data } = response.data;
      
      setEditData({
        company_name: data.company_name,
        meeting_name: data.meeting_name,
        meeting_datetime: data.meeting_datetime.slice(0, 16),
      });
      setEditingId(id);
      setEditModalOpen(true);
    } catch (err) {
      Swal.fire('오류 발생!', '회의 정보를 불러오는데 실패했습니다.', 'error');
    }
  };

  const handleEdit = async () => {
    try {
      const formData = new FormData();
      formData.append('company_name', editData.company_name);
      formData.append('meeting_name', editData.meeting_name);
      formData.append('meeting_datetime', editData.meeting_datetime);

      const response = await axios.put(
        `${import.meta.env.VITE_API_URL}/meetings/update-record/${editingId}`, 
        formData
      );
      
      if (response.data.status_code === 200) {
        await Swal.fire(
          '수정 완료!',
          '회의 정보가 성공적으로 수정되었습니다.',
          'success'
        );
        setEditModalOpen(false);
        fetchMeetings();
      } else {
        throw new Error(response.data.message);
      }
    } catch (err) {
      console.error('Edit error:', err);
      Swal.fire(
        '오류 발생!',
        err.message || '회의 정보 수정 중 오류가 발생했습니다.',
        'error'
      );
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px] text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="container mx-auto px-2 md:px-4">
      <h1 className="text-2xl md:text-3xl font-bold text-center my-4 md:my-8">회의 데이터 테이블</h1>
      
      <div className="mb-4 flex flex-col md:flex-row justify-between items-start md:items-center space-y-2 md:space-y-0">
        <select 
          className="border rounded p-1 md:p-2 text-sm md:text-base w-full md:w-auto"
          value={itemsPerPage}
          onChange={(e) => {
            setItemsPerPage(Number(e.target.value));
            setCurrentPage(1);
          }}
        >
          {[5, 15, 25, 50, 100].map(size => (
            <option key={size} value={size}>
              {size}개씩 보기
            </option>
          ))}
        </select>
        <button
          className="bg-red-500 text-white px-3 py-1 md:px-4 md:py-2 text-sm md:text-base rounded hover:bg-red-600 transition-colors w-full md:w-auto"
          onClick={handleDeleteAll}
        >
          모든 데이터 삭제
        </button>
      </div>

      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <div className="inline-block min-w-full align-middle">
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 hidden md:table border border-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">회사명</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">회의명</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">회의 일시</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">녹음 파일</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">요약본</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">전체 회의록</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-200">작업</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedMeetings.length > 0 ? (
                  paginatedMeetings.map((meeting) => (
                    <tr key={meeting.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border border-gray-200">{meeting.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border border-gray-200">{meeting.company_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border border-gray-200">{meeting.meeting_name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border border-gray-200">
                        {format(new Date(meeting.meeting_datetime), 'yyyy-MM-dd HH:mm')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 border border-gray-200">
                        <a href={meeting.wav_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          녹음 파일
                        </a>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 border border-gray-200">
                        <a href={meeting.summary_txt_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          요약본
                        </a>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 border border-gray-200">
                        <a href={meeting.whole_meeting_txt_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          전체 회의록
                        </a>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm flex space-x-2 border border-gray-200">
                        <button 
                          className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
                          onClick={() => handleEditClick(meeting.id)}
                        >
                          편집
                        </button>
                        <button 
                          className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 transition-colors"
                          onClick={() => handleDelete(meeting.id)}
                        >
                          삭제
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="px-6 py-4 text-center text-gray-500 border border-gray-200">
                      데이터가 존재하지 않습니다.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            <div className="md:hidden">
              {paginatedMeetings.length > 0 ? (
                paginatedMeetings.map((meeting) => (
                  <div key={meeting.id} className="bg-white p-3 border-b border-gray-200">
                    <div className="space-y-1.5">
                      <div>
                        <span className="text-xs font-medium text-gray-500">ID</span>
                        <p className="text-sm text-gray-900">{meeting.id}</p>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-gray-500">회사명</span>
                        <p className="text-sm text-gray-900">{meeting.company_name}</p>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-gray-500">회의명</span>
                        <p className="text-sm text-gray-900">{meeting.meeting_name}</p>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-gray-500">회의 일시</span>
                        <p className="text-sm text-gray-900">
                          {format(new Date(meeting.meeting_datetime), 'yyyy-MM-dd HH:mm')}
                        </p>
                      </div>
                      <div className="flex space-x-3">
                        <a
                          href={meeting.wav_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          녹음 파일
                        </a>
                        <a
                          href={meeting.summary_txt_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          요약본
                        </a>
                        <a
                          href={meeting.whole_meeting_txt_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          전체 회의록
                        </a>
                      </div>
                      <div className="flex space-x-2 mt-1">
                        <button 
                          className="bg-blue-500 text-white px-2 py-0.5 text-xs rounded hover:bg-blue-600 transition-colors"
                          onClick={() => handleEditClick(meeting.id)}
                        >
                          편집
                        </button>
                        <button 
                          className="bg-red-500 text-white px-2 py-0.5 text-xs rounded hover:bg-red-600 transition-colors"
                          onClick={() => handleDelete(meeting.id)}
                        >
                          삭제
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-3 text-center text-sm text-gray-500">
                  데이터가 존재하지 않습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-3 md:mt-4 flex justify-center space-x-1 md:space-x-2">
        <button
          className="px-2 md:px-4 py-1 md:py-2 text-sm md:text-base border rounded disabled:opacity-50"
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
        >
          이전
        </button>
        {[...Array(Math.min(5, pageCount))].map((_, i) => {
          let pageNum;
          if (pageCount <= 5) {
            pageNum = i + 1;
          } else {
            if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= pageCount - 2) {
              pageNum = pageCount - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }
          }
          return (
            <button
              key={pageNum}
              className={`px-2 md:px-4 py-1 md:py-2 text-sm md:text-base border rounded ${
                currentPage === pageNum ? 'bg-blue-500 text-white' : ''
              }`}
              onClick={() => setCurrentPage(pageNum)}
            >
              {pageNum}
            </button>
          );
        })}
        <button
          className="px-2 md:px-4 py-1 md:py-2 text-sm md:text-base border rounded disabled:opacity-50"
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, pageCount))}
          disabled={currentPage === pageCount}
        >
          다음
        </button>
      </div>

      {editModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">회의 정보 수정</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  회사명
                </label>
                <input
                  type="text"
                  value={editData.company_name}
                  onChange={(e) => setEditData({...editData, company_name: e.target.value})}
                  className="w-full border rounded p-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  회의명
                </label>
                <input
                  type="text"
                  value={editData.meeting_name}
                  onChange={(e) => setEditData({...editData, meeting_name: e.target.value})}
                  className="w-full border rounded p-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  회의 일시
                </label>
                <input
                  type="datetime-local"
                  value={editData.meeting_datetime}
                  onChange={(e) => setEditData({...editData, meeting_datetime: e.target.value})}
                  className="w-full border rounded p-2"
                />
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <button
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
                  onClick={() => setEditModalOpen(false)}
                >
                  취소
                </button>
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                  onClick={handleEdit}
                >
                  수정
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Table;