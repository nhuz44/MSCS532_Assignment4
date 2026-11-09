"""Regenerate an APA-style Word report and chart from this project's CSV files.

Run benchmark.py and scheduler_experiment.py first, then this script.
Requires matplotlib and python-docx (see requirements.txt). The environment
recorded in environment.txt identifies the computer that produced the results.
"""
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent


def load_csv(name):
    with (ROOT/name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def make_charts(data):
    order = ["Random", "Sorted", "Reverse sorted", "Repeated values"]
    series = ["Heapsort", "Randomized Quicksort", "Merge Sort"]
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.7), constrained_layout=True)
    for label, ax in zip(order, axs.flat):
        for algo in series:
            pairs = sorted((int(row['n']), float(row['median_time_ms']))
                           for row in data if row['algorithm'] == algo and row['dataset'] == label)
            ax.plot([p[0] for p in pairs], [p[1] for p in pairs], marker='o', linewidth=1.8, label=algo)
        ax.set_title(label, fontweight='bold')
        ax.set_xlabel('Number of elements (n)')
        ax.set_ylabel('Median execution time (ms)')
        ax.grid(alpha=.24)
        ax.legend(fontsize=7, loc='upper left')
    output = ROOT / "sorting_comparison.png"
    fig.savefig(output, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return output


def set_borders(table, color='66788A', size=9):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in('w:tblBorders')
    if borders is None:
        borders = OxmlElement('w:tblBorders')
        tbl_pr.append(borders)
    for border_name in ['top','left','bottom','right','insideH','insideV']:
        tag = 'w:' + border_name
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn('w:val'), 'single')
        element.set(qn('w:sz'), str(size))
        element.set(qn('w:color'), color)


def shade(cell, fill='EAF0F5'):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def set_cell_text(cell, value, is_heading=False):
    cell.text = str(value)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for paragraph in cell.paragraphs:
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.0
        for run in paragraph.runs:
            run.font.size = Pt(8.5)
            if is_heading:
                run.bold = True


def add_table(doc, headings, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headings))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = widths is None
    for cell, name in zip(table.rows[0].cells, headings):
        set_cell_text(cell, name, True)
        shade(cell)
    for row_data in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row_data):
            set_cell_text(cell, value)
    if widths:
        for row in table.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Inches(width)
    set_borders(table)
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        cant = OxmlElement('w:cantSplit')
        tr_pr.append(cant)
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    return table


def field_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    run._r.addnext(fld)


def paragraph(doc, text, first_indent=True, after=0):
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Inches(.5) if first_indent else Inches(0)
    p.paragraph_format.space_after = Pt(after)
    return p


def section_heading(doc, text):
    p = doc.add_paragraph(style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(text)
    return p


def small_heading(doc, text):
    p = doc.add_paragraph(style='Heading 2')
    p.add_run(text)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.style = 'Normal'
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    return p


def code(doc, lines):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(lines)
    r.font.name = 'Courier New'
    r.font.size = Pt(8)
    return p


def main():
    rows = load_csv('benchmark_results.csv')
    sr = load_csv('scheduler_results.csv')
    env = (ROOT/'environment.txt').read_text().strip().splitlines()
    environment = ', '.join(s.strip() for s in env[:3])
    png = make_charts(rows)
    by_key = {(r['algorithm'],r['dataset'],int(r['n'])):float(r['median_time_ms']) for r in rows}
    largest = max(int(r['n']) for r in rows)
    scheduler = {r['policy']:r for r in sr}
    labels = ['Random','Sorted','Reverse sorted','Repeated values']
    short = {'Heapsort':'Heap','Randomized Quicksort':'Quick','Merge Sort':'Merge'}
    comparison = [[dist,
                   f"{by_key['Heapsort',dist,largest]:.3f}",
                   f"{by_key['Randomized Quicksort',dist,largest]:.3f}",
                   f"{by_key['Merge Sort',dist,largest]:.3f}"] for dist in labels]
    rand = by_key['Heapsort','Random',largest]
    qrand = by_key['Randomized Quicksort','Random',largest]
    mrand = by_key['Merge Sort','Random',largest]
    rep = {k:by_key[k,'Repeated values',largest] for k in short}
    fastest_repeated = min(rep, key=rep.get)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(1)
    section.left_margin = section.right_margin = Inches(1)
    section.header_distance = Inches(.5)
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2.0
    normal.paragraph_format.space_after = Pt(0)
    for name in ['Heading 1','Heading 2']:
        style = doc.styles[name]
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0,0,0)
        style.paragraph_format.space_before = Pt(4)
        style.paragraph_format.space_after = Pt(2)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.line_spacing = 2.0
    field_page_number(section.header.paragraphs[0])

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(145)
    title.add_run('Heap Data Structures: Implementation, Analysis, and Applications').bold = True
    for line in ['Nhuja Shakya','University of the Cumberlands',
                 'MSCS-532-B01: Algorithms and Data Structures','Dr. Solomon',
                 'Student ID: [ENTER STUDENT ID]',
                 date.today().strftime('%B %-d, %Y')]:
        p=doc.add_paragraph(line)
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    section_heading(doc, 'Heap Data Structures: Implementation, Analysis, and Applications')
    paragraph(doc,
        'Heap data structures provide a practical connection between algorithmic complexity and task scheduling. '
        'This project implements array-based Heapsort, compares it with hand-written randomized Quicksort and Merge Sort, '
        'and builds an indexed max-heap priority queue for a small, non-preemptive infrastructure-task scheduler. '
        'The sorting and scheduling experiments were performed in Python, with automated correctness tests and repeatable inputs.')
    small_heading(doc, 'Heapsort Implementation and Invariants')
    paragraph(doc,
        'A zero-indexed Python list represents a complete binary heap: the children of index i are 2i + 1 and 2i + 2, '
        'and its parent is (i - 1) // 2. The max-heap invariant requires every parent to be at least as large as each existing child. '
        'The implementation first calls sift_down on internal nodes in reverse order, starting at n // 2 - 1, to construct a max-heap. '
        'It then repeatedly swaps the root (the maximum) with the last unsorted element and restores the heap property on the shorter prefix. '
        'This places each maximum at the end and produces ascending order without allocating a second array (Williams, 1964).')
    caption(doc,'Critical Python excerpt from heapsort.py')
    code(doc, 'for parent in range(n // 2 - 1, -1, -1):\n    _sift_down(values, parent, n)\nfor end in range(n - 1, 0, -1):\n    values[0], values[end] = values[end], values[0]\n    _sift_down(values, 0, end)')
    small_heading(doc, 'Best-, Average-, and Worst-Case Analysis')
    paragraph(doc,
        'An individual sift_down moves at most one element per tree level, so it costs O(log n). '
        'Bottom-up heap construction is tighter than multiplying that bound by n: at most n/2^(h+1) nodes occur at height h, '
        'so the sum of node costs is bounded by n times the convergent series sum(h/2^(h+1)), giving Θ(n) heap construction. '
        'Extraction performs n - 1 swaps and restores a heap of decreasing size; the total is bounded by '
        'sum from k = 2 to n of O(log k) = O(n log n). Established best- and average-case analyses also give '
        'Θ(n log n) work for conventional Heapsort; thus best, average, and worst cases are all Θ(n log n) '
        '(Schaffer & Sedgewick, 1993).')
    paragraph(doc,
        'Because the array is rearranged directly and sift_down uses iterative local variables, auxiliary space is O(1), '
        'excluding the input list itself. Heapsort is not stable: equal-valued records may change relative order. '
        'Its predictable worst-case bound is useful when latency spikes matter, while scattered parent-child accesses '
        'may reduce cache locality compared with other sorting techniques (LaMarca & Ladner, 1999).')

    small_heading(doc, 'Comparison Methodology')
    paragraph(doc,
        'Three custom Python implementations were compared: in-place max-heap Heapsort, randomized-pivot Quicksort '
        'with three-way partitioning and an explicit stack, and stable bottom-up Merge Sort. Input distributions were random, '
        'already sorted, reverse sorted, and repeated integers, at 500, 2,000, and 6,000 elements. '
        'For each configuration, seven timed trials were collected using perf_counter_ns. The same dataset was passed to '
        'each algorithm, and correctness was checked against Python sorted() after timing; input copying and a warmup run '
        'were excluded from measurement. Quicksort used a different pivot seed for each trial. '
        'These are implementation-specific wall-clock timings, not a hardware-independent ranking.')
    paragraph(doc, 'Benchmark environment: ' + environment + '. ', first_indent=False)
    caption(doc,f'Table 1. Median execution time (ms) for n = {largest}; lower is better')
    add_table(doc, ['Input distribution','Heapsort','Quicksort','Merge Sort'], comparison,
              widths=[2.2,1.2,1.2,1.2])
    caption(doc, 'Note. Quicksort uses randomized pivots and three-way partitioning; seven trials per entry.')
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing=1.0
    p.add_run().add_picture(str(png), width=Inches(6.2))
    caption(doc, 'Figure 1. Median sorting time across all tested sizes and input distributions.')

    small_heading(doc, 'Observed Performance and Explanation')
    paragraph(doc,
        f'On random inputs of {largest:,} elements, Heapsort took {rand:.3f} ms, randomized Quicksort '
        f'{qrand:.3f} ms, and Merge Sort {mrand:.3f} ms. '
        f'On repeated values at the same size, {fastest_repeated} had the lowest median '
        f'({rep[fastest_repeated]:.3f} ms); three-way Quicksort can group equal values in one partitioning step. '
        'Across the tested input distributions, Heapsort maintained the expected growth pattern without the O(n²) '
        'pivot-sensitivity of a naïve fixed-pivot Quicksort. Actual running times also reflect temporary storage, '
        'data movement, branches, Python interpreter overhead, and CPU cache behavior, which are not captured by Big-O notation '
        '(LaMarca & Ladner, 1999; Sedgewick, 1978).')

    section_heading(doc, 'Priority Queue Design and Operations')
    paragraph(doc,
        'The project represents the queue as a Python list storing immutable Task records and insertion sequence numbers. '
        'Each Task includes a unique ID, integer priority, arrival time, duration, and optional deadline. '
        'A max-heap was chosen because a higher numerical priority should be scheduled first. '
        'For equal priorities, earlier arrival and then earlier insertion win; deadline is evaluated as an outcome, '
        'rather than overriding the priority policy. This rule makes tie handling deterministic.')
    paragraph(doc,
        'An auxiliary dictionary maps task IDs to their current array indices, allowing direct lookup before a priority update. '
        'Each heap swap updates the dictionary. insert appends a task and sifts upward; extract_max replaces the root '
        'with the last entry and sifts downward; increase_key and decrease_key change one immutable task record '
        'and move it in the appropriate direction. An invalid key change, duplicate ID, or malformed Task raises an exception. '
        'These choices extend textbook binary-heap operations with efficient task-ID updates while preserving heap correctness '
        '(Python Software Foundation, n.d.).')
    caption(doc, 'Table 2. Priority queue operation complexity')
    add_table(doc, ['Operation','Time','Reason'],[
        ('insert(task)','O(log n)','Append then sift upward'),
        ('extract_max()','O(log n)','Replace root then sift downward'),
        ('increase_key()','O(log n)','Index lookup + sift upward'),
        ('decrease_key()','O(log n)','Index lookup + sift downward'),
        ('peek() / is_empty()','O(1)','Root / length check'),
    ], widths=[2.1,1.0,2.7])
    paragraph(doc,
        'Heap storage is O(n), and the task-ID index map adds O(n) storage. The mapping avoids an O(n) linear search '
        'before changing a task priority. The binary heap is well suited to frequently inserting, extracting, '
        'and re-prioritizing tasks, though unlike a sorted list it cannot efficiently enumerate all tasks in priority order '
        'without repeatedly extracting them.')

    section_heading(doc, 'Scheduler Simulation and Evaluation')
    paragraph(doc,
        'A discrete-time, non-preemptive simulator uses eight fictional IT jobs with different arrival times, '
        'priorities, durations, and deadlines. Tasks only enter the ready queue after arrival. When the current job '
        'finishes, the highest-priority ready job is selected. A FIFO baseline uses identical jobs but executes ready '
        'jobs in arrival order. Both policies are deterministic and run on the same single-worker workload. '
        'Deadline success is checked at completion, but deadlines are not used to reorder tasks.')
    cap = 'Table 3. Scheduling outcomes for identical synthetic jobs (illustrative time units)'
    caption(doc,cap)
    add_table(doc,['Metric','Max-heap priority','FIFO baseline'],[
        ('Jobs completed',scheduler['priority']['tasks'],scheduler['fifo']['tasks']),
        ('Makespan',scheduler['priority']['makespan'],scheduler['fifo']['makespan']),
        ('Mean wait',scheduler['priority']['average_wait'],scheduler['fifo']['average_wait']),
        ('Longest wait',scheduler['priority']['max_wait'],scheduler['fifo']['max_wait']),
        ('Deadline misses',scheduler['priority']['deadline_misses'],scheduler['fifo']['deadline_misses']),
    ], widths=[2.3,1.9,1.9])
    paragraph(doc,
        f'The priority scheduler produced a mean wait of {scheduler["priority"]["average_wait"]} time units, '
        f'versus {scheduler["fifo"]["average_wait"]} for FIFO. However, its longest wait was '
        f'{scheduler["priority"]["max_wait"]}, versus {scheduler["fifo"]["max_wait"]} with FIFO. '
        f'Both policies missed {scheduler["priority"]["deadline_misses"]} of '
        f'{scheduler["priority"]["deadline_count"]} deadlines. '
        'The small improvement in mean waiting time therefore came with a less favorable maximum wait; '
        'higher-priority work can delay routine tasks. It would be incorrect to conclude that priority scheduling '
        'always reduces deadlines or improves fairness. A production scheduling system might add aging, '
        'deadline-aware selection, preemption, capacity limits, and dependency validation.')
    small_heading(doc, 'Validation, Limitations, and Application')
    paragraph(doc,
        'The standard-library unittest suite checks empty and singleton lists, negative numbers, duplicates, sorted '
        'and reverse-sorted inputs, random arrays, heap-index consistency, key increases and decreases, duplicate IDs, '
        'invalid task metadata, and non-preemptive scheduling constraints. The demonstration script shows sorting and '
        'task priority changes; the scheduler writes its detailed execution trace to CSV. '
        'The scheduler is a single-resource simulation with integer durations, no interruptions, and no prerequisite graph. '
        'The task list and deadlines are artificial, and the benchmark does not measure total process memory or real '
        'server performance. For practical use, input validation, operational safeguards, fairness policies, '
        'and observed workload characteristics would need additional study.')
    section_heading(doc, 'Conclusion')
    paragraph(doc,
        'Heapsort offers consistent Θ(n log n) sorting with O(1) auxiliary space, while practical execution time '
        'depends on how an implementation interacts with data and hardware. An indexed max-heap enables O(log n) '
        'task insertion, extraction, and priority adjustment, making it suitable for configurable job selection. '
        'The scheduling experiment demonstrates that optimizing priority responsiveness can increase the wait for '
        'lower-priority work; queue design therefore requires both algorithmic efficiency and careful policy choices.')

    doc.add_page_break()
    section_heading(doc,'References')
    refs = [
        'LaMarca, A., & Ladner, R. E. (1999). The influence of caches on the performance of sorting. Journal of Algorithms, 31(1), 66–104. https://doi.org/10.1006/jagm.1998.0985',
        'Python Software Foundation. (n.d.). heapq—Heap queue algorithm. Python documentation. https://docs.python.org/3/library/heapq.html',
        'Schaffer, R., & Sedgewick, R. (1993). The analysis of heapsort. Journal of Algorithms, 15(1), 76–100. https://doi.org/10.1006/jagm.1993.1031',
        'Sedgewick, R. (1978). Implementing quicksort programs. Communications of the ACM, 21(10), 847–857. https://doi.org/10.1145/359619.359631',
        'Williams, J. W. J. (1964). Algorithm 232: Heapsort. Communications of the ACM, 7(6), 347–348. https://doi.org/10.1145/512274.512284',
    ]
    for item in refs:
        p=doc.add_paragraph(item)
        p.paragraph_format.first_line_indent=Inches(-.5)
        p.paragraph_format.left_indent=Inches(.5)
        p.paragraph_format.space_after=Pt(3)
    properties=doc.core_properties
    properties.title='Assignment 4 - Heap Data Structures: Implementation, Analysis, and Applications'
    properties.author='Nhuja Shakya'
    properties.subject='MSCS-532-B01 - Algorithms and Data Structures'
    filename = ROOT/'Assignment4_Report.docx'
    doc.save(filename)
    print('Generated:', filename)
    print('Chart:', png)
    print('Environment:', environment)


if __name__ == '__main__':
    main()
