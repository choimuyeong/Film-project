import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Suspense, lazy } from 'react';

const SearchPage = lazy(() => import('./pages/SearchPage'));
const DetailPage = lazy(() => import('./pages/DetailPage'));
const ReviewPage = lazy(() => import('./pages/ReviewPage'));

const NotFound = () => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-[#0d0d0d] text-white">
    <h2 className="text-3xl font-bold mb-4">404 - 페이지를 찾을 수 없습니다.</h2>
    <Link to="/" className="text-[#00ff88] hover:underline">홈으로 돌아가기</Link>
  </div>
);

export default function App() {
  return (
    <BrowserRouter>
      {/* 네비게이션 바 */}
      <nav className="bg-[#1a1a1a] px-8 py-4 grid grid-cols-3 items-center shadow-md sticky top-0 z-50">
        <div /> {/* 좌측 빈칸: 가운데 정렬 균형용 */}

        <Link to="/" className="text-[#00ff88] text-2xl font-bold no-underline justify-self-center">
          🎬 Movie Review AI
        </Link>

        <div className="justify-self-end">
          <Link to="/" className="text-white hover:text-[#00ff88] transition-colors no-underline">
            검색
          </Link>
        </div>
      </nav>


      <Suspense fallback={
        <div className="flex items-center justify-center min-h-screen bg-[#0d0d0d] text-white text-xl">
          영화 데이터를 불러오는 중...
        </div>
      }>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/movie/:movieId" element={<DetailPage />} />
          <Route path="/movie/:movieId/review" element={<ReviewPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>

      {/* 푸터 */}
      <footer className="text-center py-10 text-[#666] text-sm border-t border-[#333] mt-12 bg-[#0d0d0d]">
        <p>© 2026 Movie Review AI Project. Built with FastAPI & React.</p>
      </footer>
    </BrowserRouter>
  );
}