from tastypie import paginator


class NoCountPaginator(paginator.Paginator):
    """Paginator class that avoids a COUNT query and provides no total count."""
    def get_count(self):
        return 0


    def page(self):
        output = super(NoCountPaginator, self).page()
        if 'total_count' in output:
            del output['total_count']
        return output

