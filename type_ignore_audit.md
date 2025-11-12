# Type Ignore Comments Audit

## Summary
- **Total**: 65 type ignore comments
- **Status**: All tracked for future improvement
- **Goal**: Reduce to < 20 by addressing untyped external libraries

## By File (with potential improvements)

### High Priority (Many ignores, fixable)

#### 1. audio_extractor.py (13 ignores)
**Root cause**: FFmpeg and librosa lack type stubs
**Potential fixes**:
- Create stub files for FFmpeg operations
- Pin librosa version with known type patterns
- Use cast() instead of ignores where possible

#### 2. image_captioner.py (12 ignores)
**Root cause**: Transformers library (BLIP-2) is untyped
**Potential fixes**:
- Create local type stubs for transformers (transformers.pyi)
- Use cast() for model/processor returns
- Type the processor output explicitly

#### 3. api_image_captioner.py (9 ignores)
**Root cause**: API library response types unknown
**Potential fixes**:
- Create dataclass wrappers for API responses
- Use TypedDict for response structures
- Add type stubs for API libraries

### Medium Priority (Mixed ignores)

#### 4. ocr_detector.py (8 ignores)
**Root cause**: easyocr and pytesseract lack type stubs
**Potential fixes**:
- Create type stubs (stubs/easyocr.pyi, stubs/pytesseract.pyi)
- Already using cast() - could improve with better stubs
- Create OCR result wrapper types

#### 5. transcriber.py (6 ignores)
**Root cause**: Whisper internal API, openai-whisper lacks stubs
**Potential fixes**:
- Create whisper.pyi stub file (stubs/whisper.pyi)
- Wrap internal functions with typed interfaces
- Use cast() more strategically

#### 6. error_handling.py (5 ignores)
**Root cause**: Various library validation issues
**Potential fixes**:
- Review each ignore individually - some may be unnecessary
- Use TypeGuard for isinstance checks

#### 7. frame_analyzer.py (5 ignores)
**Root cause**: Protected member access (intentional)
**Status**: These are architectural and OK
**Note**: Could be eliminated by making methods public or creating public interface

### Low Priority (Minimal ignores)

#### 8. visual_analyzer.py (2 ignores)
**Root cause**: OpenCV quirks
**Status**: Easy to document and acceptable

#### 9. cli.py (2 ignores)
**Root cause**: Typer/external integration
**Status**: Could be reduced with better type patterns

#### 10. gradio_app.py (2 ignores)
**Root cause**: Gradio themes not in stubs
**Status**: Acceptable, wait for Gradio typing improvements

#### 11. object_detector.py (1 ignore)
**Status**: Minimal, not a priority

---

## Action Items for Future Sessions

### Phase 1: Create Type Stubs (Biggest impact)
- [ ] Create `stubs/transformers.pyi` (eliminates 12 ignores in image_captioner.py)
- [ ] Create `stubs/whisper.pyi` (eliminates 6 ignores in transcriber.py)
- [ ] Create `stubs/easyocr.pyi` (eliminates 4 ignores in ocr_detector.py)
- [ ] Create `stubs/pytesseract.pyi` (eliminates 4 ignores in ocr_detector.py)

### Phase 2: Refactor Libraries
- [ ] audio_extractor.py: Create FFmpeg wrapper with types
- [ ] image_captioner.py: Wrap transformer results
- [ ] api_image_captioner.py: Create typed API response wrappers

### Phase 3: Architecture Improvements
- [ ] frame_analyzer.py: Make protected methods public or create public interface
- [ ] Review all "reportPrivateUsage" ignores - may indicate design issue

---

## Type Ignore Distribution by Rule

| Rule | Count | Fixability |
|------|-------|-----------|
| Generic (no rule) | 30 | Requires stubs |
| reportUnknownMemberType | 12 | Requires stubs |
| attr-defined | 6 | Requires stubs |
| reportPrivateUsage | 4 | Architecture change |
| arg-type | 4 | Better type handling |
| import-untyped | 1 | Requires stubs |

---

## Success Metrics

- [ ] **Goal**: < 20 ignores total
- [ ] **Target**: Eliminate all generic "# type: ignore" (30 currently)
- [ ] **Stretch**: Make all remaining ignores specific rules
- [ ] **Ultimate**: < 10 ignores (likely unachievable without upstream changes)

---

Generated: 2025-11-12
Status: All 303 type errors fixed, tracking 65 strategic type ignores
